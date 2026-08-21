# ASP.NET Core Error Simulation Server

A zero-dependency Python server that generates believable ASP.NET Core-style failures for development, testing, research, screenshots, log viewers, and error-state simulation.

The output follows a normal backend architecture instead of filling every line with nonsense:

```text
Northwind.Store.Api.Controllers.OrdersController
Northwind.Store.Application.Services.OrderService
Northwind.Store.Infrastructure.Persistence.OrderRepository
Microsoft.EntityFrameworkCore.DbContext.SaveChangesAsync(...)
Microsoft.Data.SqlClient.SqlCommand.ExecuteDbDataReaderAsync(...)
Microsoft.AspNetCore.Mvc.Infrastructure.ControllerActionInvoker...
Microsoft.AspNetCore.Authorization.AuthorizationMiddleware...
```

The old absurdity is now optional. `--chaos 1-7` stays mostly realistic; only `8-10` occasionally leaks a weird token into a message.

## Requirements

Python 3.10+ recommended. No third-party packages.

## Start

```bash
python fake_dotnet_server.py
```

Default address:

```text
http://127.0.0.1:8000
```

## ASP.NET-style page

```bash
python fake_dotnet_server.py --dotnet
```

Visit:

```text
http://127.0.0.1:8000/
```

The page shows a developer exception with a realistic application stack, ASP.NET Core middleware, trace IDs, query parameters, headers, and scenario-specific diagnostics.

Authorization and Cookie headers are redacted.

## Profiles

Choose the type of application:

```text
commerce
payments
identity
saas
```

Examples:

```bash
python fake_dotnet_server.py --dotnet --profile commerce
python fake_dotnet_server.py --dotnet --profile payments
python fake_dotnet_server.py --dotnet --profile identity
python fake_dotnet_server.py --dotnet --profile saas
```

Profiles change the namespaces and application layers. For example, the payments profile uses names like:

```text
Contoso.Payments.Api.Controllers.PaymentsController
Contoso.Payments.Application.Services.PaymentService
Contoso.Payments.Infrastructure.Persistence.PaymentRepository
```

## Failure scenarios

Available:

```text
random
ef
sql
http
auth
validation
redis
startup
timeout
nullref
```

### Entity Framework

```bash
python fake_dotnet_server.py --dotnet --scenario ef
```

Possible shape:

```text
Microsoft.EntityFrameworkCore.DbUpdateException:
An error occurred while saving the entity changes.

 ---> Microsoft.Data.SqlClient.SqlException:
Violation of UNIQUE KEY constraint 'UX_Orders_ExternalId'.
```

### SQL Server

```bash
python fake_dotnet_server.py --dotnet --scenario sql
```

Generated SQL errors can include realistic categories such as duplicate keys, foreign-key failures, deadlock victims, and command timeouts.

### HttpClient / downstream service

```bash
python fake_dotnet_server.py --dotnet --scenario http --status 503
```

The generated page may show a dependency like:

```text
https://inventory.internal/api/v1/reservations
```

### Redis

```bash
python fake_dotnet_server.py --dotnet --scenario redis
```

Example:

```text
StackExchange.Redis.RedisTimeoutException:
Timeout awaiting response (outbound=0KiB, inbound=0KiB, 5000ms elapsed).
```

### Authentication

```bash
python fake_dotnet_server.py \
  --dotnet \
  --scenario auth \
  --respect-scenario-status
```

This can return 401 or 403 instead of forcing the default 500.

### Validation

```bash
python fake_dotnet_server.py \
  --scenario validation \
  --respect-scenario-status
```

Returns 400.

### Dependency injection / startup

```bash
python fake_dotnet_server.py --dotnet --scenario startup
```

Example:

```text
System.InvalidOperationException:
Unable to resolve service for type
'Northwind.Store.Infrastructure.IClock'
while attempting to activate
'Northwind.Store.Api.Controllers.OrdersController'.
```

## Endpoints

### `/`

Main generated error. HTML when `--dotnet` is enabled, plain text otherwise.

### `/stack`

Generated stack trace.

### `/exception`

Generated exception and stack trace.

### `/api/error`

ProblemDetails-style JSON:

```json
{
  "type": "https://httpstatuses.com/500",
  "title": "An unexpected error occurred.",
  "status": 500,
  "detail": "Execution Timeout Expired.",
  "instance": "/api/error",
  "traceId": "00-..."
}
```

To include the generated exception and stack trace:

```bash
python fake_dotnet_server.py --include-stack-json
```

### `/health`

Healthy JSON response:

```json
{
  "status": "Healthy",
  "service": "Store API",
  "environment": "Development",
  "version": "1.14.3"
}
```

### `/api/scenario`

Shows the active profile and generated scenario.

## Recommended commands

Believable commerce/EF failure:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --profile commerce \
  --scenario ef
```

Payments API with a downstream outage:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --profile payments \
  --scenario http \
  --status 503
```

Identity API auth failure:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --profile identity \
  --scenario auth \
  --respect-scenario-status
```

SaaS application Redis timeout:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --profile saas \
  --scenario redis
```

A randomized backend:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --profile commerce \
  --scenario random
```

## Optional weirdness

Default:

```text
--chaos 2
```

`1-7` stays essentially realistic.

At `8-10`, a small amount of the original Unicode weirdness can leak into exception messages:

```bash
python fake_dotnet_server.py \
  --dotnet \
  --scenario ef \
  --chaos 10
```

The stack itself remains structured as a plausible .NET stack.

## Status codes

Errors return 500 by default:

```bash
python fake_dotnet_server.py --status 503
```

To allow auth and validation scenarios to pick sensible statuses:

```bash
python fake_dotnet_server.py --respect-scenario-status
```

This enables:

```text
validation -> 400
auth       -> 401 or 403
most others -> 500
```

## CLI

```bash
python fake_dotnet_server.py --help
```

Main options:

```text
--dotnet
--profile {commerce,payments,identity,saas}
--scenario {random,ef,sql,http,auth,validation,redis,startup,timeout,nullref}
--status STATUS
--respect-scenario-status
--include-stack-json
--chaos 1-10
--version VERSION
--host HOST
--port PORT
--seed SEED
```

## LAN use

The default is loopback only:

```text
127.0.0.1
```

For deliberate LAN testing:

```bash
python fake_dotnet_server.py --host 0.0.0.0 --dotnet
```

## Files

```text
plausible_dotnet_fake_server/
├── fake_dotnet_server.py
└── README.md
```
