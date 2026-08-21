#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import random
import secrets
import sys
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


APP_PROFILES = {
    "commerce": {
        "assembly": "Northwind.Store.Api",
        "root_namespace": "Northwind.Store",
        "service": "Store API",
        "controllers": ["OrdersController", "CheckoutController", "ProductsController", "CustomersController"],
        "services": ["OrderService", "CheckoutService", "CatalogService", "CustomerService"],
        "repositories": ["OrderRepository", "ProductRepository", "CustomerRepository"],
    },
    "payments": {
        "assembly": "Contoso.Payments.Api",
        "root_namespace": "Contoso.Payments",
        "service": "Payments API",
        "controllers": ["PaymentsController", "RefundsController", "WebhooksController", "PaymentMethodsController"],
        "services": ["PaymentService", "RefundService", "WebhookService", "PaymentMethodService"],
        "repositories": ["PaymentRepository", "RefundRepository", "MerchantRepository"],
    },
    "identity": {
        "assembly": "Fabrikam.Identity.Api",
        "root_namespace": "Fabrikam.Identity",
        "service": "Identity API",
        "controllers": ["SessionsController", "UsersController", "TokensController", "PasswordController"],
        "services": ["SessionService", "UserService", "TokenService", "PasswordResetService"],
        "repositories": ["UserRepository", "SessionRepository", "TokenRepository"],
    },
    "saas": {
        "assembly": "Acme.Platform.Api",
        "root_namespace": "Acme.Platform",
        "service": "Platform API",
        "controllers": ["ProjectsController", "MembersController", "BillingController", "IntegrationsController"],
        "services": ["ProjectService", "MemberService", "BillingService", "IntegrationService"],
        "repositories": ["ProjectRepository", "MembershipRepository", "IntegrationRepository"],
    },
}

SCENARIOS = ("ef", "sql", "http", "auth", "validation", "redis", "startup", "timeout", "nullref")

EXCEPTIONS = {
    "ef": [
        ("Microsoft.EntityFrameworkCore.DbUpdateException",
         "An error occurred while saving the entity changes. See the inner exception for details."),
        ("System.InvalidOperationException",
         "The instance of entity type 'Order' cannot be tracked because another instance with the same key value is already being tracked."),
    ],
    "sql": [
        ("Microsoft.Data.SqlClient.SqlException",
         "Execution Timeout Expired. The timeout period elapsed prior to completion of the operation or the server is not responding."),
        ("Microsoft.Data.SqlClient.SqlException",
         "Violation of UNIQUE KEY constraint 'UX_Orders_ExternalId'. Cannot insert duplicate key in object 'dbo.Orders'."),
    ],
    "http": [
        ("System.Net.Http.HttpRequestException", "Connection refused (inventory.internal:8080)"),
        ("System.Threading.Tasks.TaskCanceledException",
         "The request was canceled due to the configured HttpClient.Timeout of 10 seconds elapsing."),
    ],
    "auth": [
        ("Microsoft.IdentityModel.Tokens.SecurityTokenExpiredException",
         "IDX10223: Lifetime validation failed. The token is expired."),
        ("System.UnauthorizedAccessException",
         "The current principal is not authorized to perform this operation."),
    ],
    "validation": [
        ("FluentValidation.ValidationException",
         "Validation failed: -- Email: 'Email' is not a valid email address."),
        ("System.ArgumentException",
         "The supplied request contains an invalid state transition."),
    ],
    "redis": [
        ("StackExchange.Redis.RedisTimeoutException",
         "Timeout awaiting response (outbound=0KiB, inbound=0KiB, 5000ms elapsed)."),
        ("StackExchange.Redis.RedisConnectionException",
         "No connection is active/available to service this operation."),
    ],
    "startup": [
        ("System.InvalidOperationException",
         "Unable to resolve service for type 'Northwind.Store.Infrastructure.IClock' while attempting to activate 'Northwind.Store.Api.Controllers.OrdersController'."),
        ("Microsoft.Extensions.Options.OptionsValidationException",
         "DataAnnotation validation failed for 'DatabaseOptions' members: 'ConnectionString' with the error: 'The ConnectionString field is required.'."),
    ],
    "timeout": [
        ("System.TimeoutException", "The operation has timed out."),
        ("System.OperationCanceledException", "The operation was canceled."),
    ],
    "nullref": [
        ("System.NullReferenceException", "Object reference not set to an instance of an object."),
    ],
}

SQL_ERRORS = [
    ("2627", "Violation of UNIQUE KEY constraint 'UX_Orders_ExternalId'. Cannot insert duplicate key in object 'dbo.Orders'."),
    ("547", "The INSERT statement conflicted with the FOREIGN KEY constraint 'FK_OrderItems_Orders_OrderId'."),
    ("1205", "Transaction (Process ID 91) was deadlocked on lock resources with another process and has been chosen as the deadlock victim."),
    ("-2", "Execution Timeout Expired. The timeout period elapsed prior to completion of the operation."),
]

HTTP_DEPENDENCIES = [
    "https://inventory.internal/api/v1/reservations",
    "https://pricing.internal/api/v2/quote",
    "https://identity.internal/connect/introspect",
    "https://notifications.internal/api/messages",
]

MVC_FRAMES = [
    "Microsoft.AspNetCore.Mvc.Infrastructure.ControllerActionInvoker.InvokeActionMethodAsync()",
    "Microsoft.AspNetCore.Mvc.Infrastructure.ControllerActionInvoker.InvokeNextActionFilterAsync()",
    "Microsoft.AspNetCore.Mvc.Infrastructure.ResourceInvoker.InvokeFilterPipelineAsync()",
]

MIDDLEWARE_FRAMES = [
    "Microsoft.AspNetCore.Authorization.AuthorizationMiddleware.Invoke(HttpContext context)",
    "Microsoft.AspNetCore.Authentication.AuthenticationMiddleware.Invoke(HttpContext context)",
    "Microsoft.AspNetCore.Routing.EndpointMiddleware.Invoke(HttpContext httpContext)",
    "Microsoft.AspNetCore.Diagnostics.DeveloperExceptionPageMiddlewareImpl.Invoke(HttpContext context)",
]

EF_FRAMES = [
    "Microsoft.EntityFrameworkCore.Update.ReaderModificationCommandBatch.ExecuteAsync(IRelationalConnection connection, CancellationToken cancellationToken)",
    "Microsoft.EntityFrameworkCore.Update.Internal.BatchExecutor.ExecuteAsync(IEnumerable`1 commandBatches, IRelationalConnection connection, CancellationToken cancellationToken)",
    "Microsoft.EntityFrameworkCore.ChangeTracking.Internal.StateManager.SaveChangesAsync(IList`1 entriesToSave, CancellationToken cancellationToken)",
    "Microsoft.EntityFrameworkCore.DbContext.SaveChangesAsync(Boolean acceptAllChangesOnSuccess, CancellationToken cancellationToken)",
]

SQL_FRAMES = [
    "Microsoft.Data.SqlClient.SqlCommand.ExecuteDbDataReaderAsync(CommandBehavior behavior, CancellationToken cancellationToken)",
    "Microsoft.Data.SqlClient.SqlConnection.OnError(SqlException exception, Boolean breakConnection, Action`1 wrapCloseInAction)",
]

REDIS_FRAMES = [
    "StackExchange.Redis.ConnectionMultiplexer.ExecuteSyncImpl[T](Message message, ResultProcessor`1 processor, ServerEndPoint server, T defaultValue)",
    "StackExchange.Redis.RedisDatabase.StringGetAsync(RedisKey key, CommandFlags flags)",
]

SOURCE_ROOTS = [r"C:\src", r"D:\agent\_work\1\s", "/home/vsts/work/1/s", "/app/src"]
WEIRD = ["banana", "Kartoffel", "𓆏", "fromage", "月", "жабка", "🧀", "orb"]


def trace_id():
    return f"00-{secrets.token_hex(16)}-{secrets.token_hex(8)}-01"


def activity_id():
    return secrets.token_hex(8)


def esc(v):
    return html.escape(str(v), quote=True)


def maybe_weird(text, chaos):
    if chaos >= 8 and random.random() < (chaos - 7) * 0.12:
        return text + f" [{random.choice(WEIRD)}]"
    return text


def app_frame(profile, layer):
    root = profile["root_namespace"]
    if layer == "controller":
        ns = f"{root}.Api.Controllers"
        cls = random.choice(profile["controllers"])
        method = random.choice(["Get", "Post", "Create", "Update"])
    elif layer == "service":
        ns = f"{root}.Application.Services"
        cls = random.choice(profile["services"])
        method = random.choice(["ExecuteAsync", "CreateAsync", "GetAsync", "ProcessAsync"])
    else:
        ns = f"{root}.Infrastructure.Persistence"
        cls = random.choice(profile["repositories"])
        method = random.choice(["SaveAsync", "GetByIdAsync", "InsertAsync", "UpdateAsync"])

    root_path = random.choice(SOURCE_ROOTS)
    file_path = f"{root_path}/{profile['assembly'].replace('.', '/')}/{cls}.cs".replace("//", "/")
    return f"   at {ns}.{cls}.{method}(...) in {file_path}:line {random.randint(24, 240)}"


def build_error(profile, scenario, chaos):
    exc_type, message = random.choice(EXCEPTIONS[scenario])
    if scenario == "startup":
        message = message.replace("Northwind.Store", profile["root_namespace"])
    data = {
        "scenario": scenario,
        "type": exc_type,
        "message": maybe_weird(message, chaos),
        "trace_id": trace_id(),
        "activity_id": activity_id(),
        "status": 500,
        "inner": [],
        "dependency": None,
        "database": None,
    }

    if scenario == "validation":
        data["status"] = 400
    elif scenario == "auth":
        data["status"] = random.choice([401, 403])

    if scenario in ("ef", "sql"):
        num, inner_message = random.choice(SQL_ERRORS)
        data["inner"].append({
            "type": "Microsoft.Data.SqlClient.SqlException",
            "message": inner_message,
            "number": num,
        })
        data["database"] = {
            "server": "sql-primary.internal,1433",
            "database": random.choice(["Store", "Payments", "Identity", "Platform"]),
            "commandTimeoutSeconds": random.choice([15, 30, 60]),
            "sqlErrorNumber": num,
        }

    if scenario == "http":
        data["dependency"] = {
            "method": random.choice(["GET", "POST"]),
            "uri": random.choice(HTTP_DEPENDENCIES),
            "timeoutSeconds": random.choice([5, 10, 30]),
        }
    elif scenario == "redis":
        data["dependency"] = {
            "endpoint": "redis.internal:6379",
            "database": random.randint(0, 3),
            "operation": random.choice(["GET session:9d2e", "SET cache:product:4821", "HGET tenant:1182 plan"]),
        }

    frames = [app_frame(profile, "controller"), app_frame(profile, "service")]

    if scenario in ("ef", "sql"):
        frames.append(app_frame(profile, "repository"))
        frames.extend("   at " + x for x in EF_FRAMES)
        frames.extend("   at " + x for x in SQL_FRAMES)
    elif scenario == "http":
        frames.extend([
            "   at System.Net.Http.HttpConnection.SendAsync(HttpRequestMessage request, Boolean async, CancellationToken cancellationToken)",
            "   at System.Net.Http.HttpClient.SendAsync(HttpRequestMessage request, HttpCompletionOption completionOption, CancellationToken cancellationToken)",
        ])
    elif scenario == "redis":
        frames.extend("   at " + x for x in REDIS_FRAMES)
    elif scenario == "auth":
        frames.extend([
            "   at Microsoft.AspNetCore.Authentication.JwtBearer.JwtBearerHandler.HandleAuthenticateAsync()",
            "   at Microsoft.AspNetCore.Authentication.AuthenticationHandler`1.AuthenticateAsync()",
        ])
    elif scenario == "validation":
        frames.extend([
            "   at FluentValidation.AbstractValidator`1.ValidateAsync(ValidationContext`1 context, CancellationToken cancellation)",
            "   at FluentValidation.AspNetCore.FluentValidationObjectModelValidator.Validate(...)",
        ])
    elif scenario == "startup":
        frames = [
            "   at Microsoft.Extensions.DependencyInjection.ActivatorUtilities.ThrowHelperUnableToResolveService(Type type, Type requiredBy)",
            "   at Microsoft.Extensions.DependencyInjection.ActivatorUtilities.CreateInstance(IServiceProvider provider, Type instanceType, Object[] parameters)",
            "   at Microsoft.AspNetCore.Mvc.Controllers.ControllerFactoryProvider.CreateControllerFactory(ControllerActionDescriptor descriptor)",
        ]
    elif scenario == "timeout":
        frames.append("   at System.Threading.CancellationToken.ThrowOperationCanceledException()")
    elif scenario == "nullref":
        frames.append(app_frame(profile, "repository"))

    frames.extend("   at " + x for x in MVC_FRAMES)
    frames.extend("   at " + x for x in MIDDLEWARE_FRAMES[:3])
    data["stack"] = "\n".join(frames)

    lines = [f"{data['type']}: {data['message']}", data["stack"]]
    for inner in data["inner"]:
        lines += [
            f" ---> {inner['type']}: {inner['message']}",
            "   at Microsoft.Data.SqlClient.SqlConnection.OnError(SqlException exception, Boolean breakConnection, Action`1 wrapCloseInAction)",
            "   at Microsoft.Data.SqlClient.TdsParser.ThrowExceptionAndWarning(...)",
            "   --- End of inner exception stack trace ---",
        ]
    data["text"] = "\n".join(lines)
    return data


def render_page(handler, profile, data):
    parsed = urlparse(handler.path)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query_rows = "".join(
        f"<tr><td>{esc(k)}</td><td>{esc(', '.join(v))}</td></tr>" for k, v in query.items()
    ) or "<tr><td colspan='2'><em>No query parameters</em></td></tr>"

    headers = []
    for k, v in handler.headers.items():
        if k.lower() in ("authorization", "cookie"):
            v = "[redacted]"
        headers.append((k, v))
    header_rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in headers)

    dep = ""
    if data["dependency"]:
        dep = f"<section class='card'><h2>Dependency</h2><pre>{esc(json.dumps(data['dependency'], indent=2))}</pre></section>"

    db = ""
    if data["database"]:
        db = f"<section class='card'><h2>Database</h2><pre>{esc(json.dumps(data['database'], indent=2))}</pre></section>"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(data["type"])} - {esc(profile["service"])}</title>
<style>
:root{{--bg:#111318;--panel:#1a1e25;--border:#343b47;--text:#eef1f5;--muted:#a8b0bd;--danger:#ff6b6b;--code:#0d0f13}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}}
header{{padding:28px 32px 20px;border-bottom:1px solid var(--border)}}main{{max-width:1180px;margin:auto;padding:24px}}
h1{{color:var(--danger);font-size:1.45rem;margin:0 0 8px;overflow-wrap:anywhere}}h2{{font-size:1rem;margin:0 0 12px}}
.meta{{color:var(--muted);font-size:.9rem}}.card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px;margin:16px 0}}
pre{{margin:0;background:var(--code);padding:14px;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.5 ui-monospace,Consolas,monospace}}
table{{width:100%;border-collapse:collapse}}td{{padding:7px 9px;border-bottom:1px solid var(--border);vertical-align:top;overflow-wrap:anywhere}}
td:first-child{{width:230px;color:var(--muted);font-family:ui-monospace,Consolas,monospace}}
footer{{color:var(--muted);font-size:.82rem;padding:8px 0 28px}}
</style></head><body>
<header><h1>{esc(data["type"])}</h1><div>{esc(data["message"])}</div>
<div class="meta">{esc(profile["assembly"])} · Microsoft.AspNetCore.App 8.0.x · Development</div></header>
<main>
<section class="card"><h2>Stack Trace</h2><pre>{esc(data["text"])}</pre></section>
{dep}{db}
<section class="card"><h2>Request</h2><table>
<tr><td>Method</td><td>{esc(handler.command)}</td></tr>
<tr><td>Path</td><td>{esc(parsed.path)}</td></tr>
<tr><td>Protocol</td><td>{esc(handler.request_version)}</td></tr>
<tr><td>TraceIdentifier</td><td>{esc(data["trace_id"])}</td></tr>
<tr><td>ActivityId</td><td>{esc(data["activity_id"])}</td></tr>
<tr><td>TimestampUtc</td><td>{esc(datetime.now(timezone.utc).isoformat())}</td></tr>
</table></section>
<section class="card"><h2>Query</h2><table>{query_rows}</table></section>
<section class="card"><h2>Headers</h2><table>{header_rows}</table></section>
<footer>ASP.NET Core development diagnostics</footer>
</main></body></html>"""


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, addr, handler, args):
        super().__init__(addr, handler)
        self.args = args
        self.counter = 0
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server_version = "Kestrel"
    sys_version = ""

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s %s\n" % (datetime.now().strftime("%H:%M:%S"), self.client_address[0], fmt % args))

    def seed_request(self):
        if self.server.args.seed is None:
            random.seed(secrets.randbits(64))
        else:
            with self.server.lock:
                self.server.counter += 1
                n = self.server.counter
            random.seed(f"{self.server.args.seed}:{n}:{self.command}:{self.path}")

    def send_body(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def handle_all(self):
        self.seed_request()
        a = self.server.args
        profile = APP_PROFILES[a.profile]
        scenario = random.choice(SCENARIOS) if a.scenario == "random" else a.scenario
        data = build_error(profile, scenario, a.chaos)
        path = urlparse(self.path).path

        if path == "/health":
            body = json.dumps({
                "status": "Healthy", "service": profile["service"],
                "environment": "Development", "version": a.version
            }, indent=2).encode()
            return self.send_body(200, body, "application/json; charset=utf-8")

        if path == "/api/scenario":
            body = json.dumps({
                "profile": a.profile, "scenario": scenario,
                "availableScenarios": list(SCENARIOS), "dotnet": a.dotnet
            }, indent=2).encode()
            return self.send_body(200, body, "application/json; charset=utf-8")

        if path == "/api/error":
            status = data["status"] if a.respect_scenario_status else a.status
            payload = {
                "type": f"https://httpstatuses.com/{status}",
                "title": {400:"One or more validation errors occurred.",401:"Unauthorized",403:"Forbidden",500:"An unexpected error occurred.",503:"Service Unavailable"}.get(status, "Request failed."),
                "status": status,
                "detail": data["message"],
                "instance": path,
                "traceId": data["trace_id"],
            }
            if a.include_stack_json:
                payload["exception"] = data["type"]
                payload["stackTrace"] = data["text"]
            return self.send_body(status, json.dumps(payload, indent=2).encode(), "application/problem+json; charset=utf-8")

        if path in ("/", "/stack", "/exception"):
            status = data["status"] if a.respect_scenario_status else a.status
            if a.dotnet:
                return self.send_body(status, render_page(self, profile, data).encode(), "text/html; charset=utf-8")
            return self.send_body(status, data["text"].encode(), "text/plain; charset=utf-8")

        payload = {"type":"https://httpstatuses.com/404","title":"Not Found","status":404,
                   "detail":f"No endpoint matches '{path}'.","traceId":trace_id()}
        self.send_body(404, json.dumps(payload, indent=2).encode(), "application/problem+json; charset=utf-8")

    do_GET = handle_all
    do_POST = handle_all
    do_PUT = handle_all
    do_PATCH = handle_all
    do_DELETE = handle_all
    do_HEAD = handle_all


def args():
    p = argparse.ArgumentParser(description="ASP.NET Core error simulation server for development and testing.")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--dotnet", action="store_true", help="Render ASP.NET Core-style HTML developer exception pages.")
    p.add_argument("--profile", choices=sorted(APP_PROFILES), default="commerce")
    p.add_argument("--scenario", choices=("random",)+SCENARIOS, default="random")
    p.add_argument("--status", type=int, default=500)
    p.add_argument("--respect-scenario-status", action="store_true")
    p.add_argument("--include-stack-json", action="store_true")
    p.add_argument("--chaos", type=int, default=2, help="1-10; values below 8 remain realistic.")
    p.add_argument("--seed", type=int)
    p.add_argument("--version", default="1.14.3")
    return p.parse_args()


def main():
    a = args()
    a.chaos = max(1, min(10, a.chaos))
    if not 1 <= a.port <= 65535:
        raise SystemExit("--port must be 1-65535")
    if not 100 <= a.status <= 599:
        raise SystemExit("--status must be 100-599")

    server = Server((a.host, a.port), Handler, a)
    print(f"{APP_PROFILES[a.profile]['service']} development server")
    print(f"Listening on http://{a.host}:{a.port}")
    print(f"profile={a.profile} scenario={a.scenario} dotnet={a.dotnet} chaos={a.chaos}")
    print("Endpoints: / /health /stack /exception /api/error /api/scenario")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
