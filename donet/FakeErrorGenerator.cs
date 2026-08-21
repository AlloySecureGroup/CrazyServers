using System.Net;
using System.Text;

namespace DecoyServer;

/// <summary>
/// Produces fake ASP.NET "Yellow Screen of Death" error pages. Every frame is
/// assembled at random from real-looking framework symbols mixed with fabricated
/// application symbols, so the trace reads as plausible at a glance but describes
/// no real code path. Used as a honeypot / deception surface to waste the time of
/// automated scanners and manual pokers probing for a genuine .NET Framework app.
/// </summary>
public sealed class FakeErrorGenerator
{
    private readonly Random _rng = new();

    private static readonly (string Type, string Message)[] Exceptions =
    {
        ("System.NullReferenceException", "Object reference not set to an instance of an object."),
        ("System.InvalidOperationException", "The connection was not closed. The connection's current state is open."),
        ("System.Data.SqlClient.SqlException", "Timeout expired.  The timeout period elapsed prior to completion of the operation or the server is not responding."),
        ("System.ArgumentNullException", "Value cannot be null. (Parameter 'source')"),
        ("System.IndexOutOfRangeException", "Index was outside the bounds of the array."),
        ("System.InvalidCastException", "Unable to cast object of type 'System.Int64' to type 'System.String'."),
        ("System.FormatException", "Input string was not in a correct format."),
        ("System.Web.HttpException", "Request timed out."),
        ("System.Threading.Tasks.TaskCanceledException", "A task was canceled."),
        ("System.ObjectDisposedException", "Cannot access a disposed object.\r\nObject name: 'System.Data.SqlClient.SqlConnection'."),
        ("Newtonsoft.Json.JsonSerializationException", "Unexpected token when deserializing object: StartArray. Path 'items', line 1, position 14."),
        ("System.Data.Entity.Core.EntityCommandExecutionException", "An error occurred while executing the command definition. See the inner exception for details."),
        ("System.Configuration.ConfigurationErrorsException", "The requested configuration section cannot be used because it is not declared."),
    };

    // A blend of real framework namespaces and clearly fictional application ones
    // (Contoso is Microsoft's canonical placeholder company, so it can never be
    // mistaken for a real product).
    private static readonly string[] Namespaces =
    {
        "System.Web.UI",
        "System.Web.UI.WebControls",
        "System.Web.Mvc",
        "System.Web.Http.Controllers",
        "System.Data.SqlClient",
        "System.Data.Entity.Core.Objects",
        "Microsoft.EntityFrameworkCore.Query.Internal",
        "System.Runtime.CompilerServices",
        "System.Threading.Tasks",
        "Newtonsoft.Json.Serialization",
        "Contoso.Web.Controllers",
        "Contoso.Services.Billing",
        "Contoso.Data.Repositories",
        "Contoso.Domain.Accounts",
        "Contoso.Infrastructure.Caching",
    };

    private static readonly string[] Classes =
    {
        "Page", "TemplateControl", "HttpApplication", "ControllerActionInvoker",
        "ReflectedActionDescriptor", "SqlCommand", "SqlConnection", "ObjectContext",
        "QueryCompiler", "AsyncMethodBuilderCore", "JsonSerializerInternalReader",
        "AccountController", "InvoiceController", "BillingService", "PaymentGateway",
        "CustomerRepository", "UnitOfWork", "CacheManager", "TokenValidator",
        "LedgerProjection",
    };

    private static readonly string[] Methods =
    {
        "ProcessRequest", "HandleError", "ExecuteStepImpl", "InvokeActionMethod",
        "GetParameterValues", "ExecuteReader", "ExecuteNonQuery", "Open",
        "MaterializeEntity", "CompileQuery", "MoveNext", "Start", "Deserialize",
        "ReadObject", "Index", "Details", "ChargeCard", "GetById", "Commit",
        "Resolve", "Validate", "LoadFromCache", "Reconcile",
    };

    private static readonly string[] Parameters =
    {
        "",
        "HttpContext context",
        "Exception e",
        "Int32 index",
        "String key, Boolean throwOnMissing",
        "Object value, Type objectType",
        "CancellationToken cancellationToken",
        "Guid entityId",
        "IDbCommand command, CommandBehavior behavior",
        "ActionExecutingContext filterContext",
        "IDictionary`2 parameters",
    };

    private static readonly string[] SourceFiles =
    {
        @"c:\inetpub\wwwroot\Contoso.Web\Controllers\AccountController.cs",
        @"c:\inetpub\wwwroot\Contoso.Web\Services\BillingService.cs",
        @"c:\inetpub\wwwroot\Contoso.Web\Data\CustomerRepository.cs",
        @"D:\Build\agent\_work\1\s\src\Contoso.Domain\Accounts\AccountAggregate.cs",
        @"D:\Build\agent\_work\1\s\src\Contoso.Infrastructure\Caching\CacheManager.cs",
    };

    private static readonly string[] SourceSnippets =
    {
        "Line 40:            var account = _repository.GetById(id);\r\n" +
        "Line 41:            var balance = account.Ledger.CurrentBalance;\r\n" +
        "Line 42:            return View(balance.ToStatement());\r\n",

        "Line 87:            using (var reader = command.ExecuteReader())\r\n" +
        "Line 88:            {\r\n" +
        "Line 89:                while (reader.Read()) { yield return Map(reader); }\r\n",

        "Line 12:        public decimal Reconcile(Guid entityId)\r\n" +
        "Line 13:        {\r\n" +
        "Line 14:            return _entries.Sum(e => e.Amount) - _holds.Total;\r\n",
    };

    /// <summary>Builds a full HTML error page for the given request path.</summary>
    public string BuildPage(string requestPath)
    {
        var ex = Exceptions[_rng.Next(Exceptions.Length)];
        var snippet = SourceSnippets[_rng.Next(SourceSnippets.Length)];
        var sourceFile = SourceFiles[_rng.Next(SourceFiles.Length)];
        var sourceLine = _rng.Next(11, 512);
        var trace = BuildStackTrace(ex.Type, ex.Message);

        var encodedType = WebUtility.HtmlEncode(ex.Type);
        var encodedMessage = WebUtility.HtmlEncode(ex.Message);
        var encodedSnippet = WebUtility.HtmlEncode(snippet);
        var encodedFile = WebUtility.HtmlEncode(sourceFile);
        var encodedTrace = WebUtility.HtmlEncode(trace);

        var page = new StringBuilder(8192);
        page.Append("<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\r\n");
        page.Append("<html xmlns=\"http://www.w3.org/1999/xhtml\">\r\n");
        page.Append("    <head>\r\n");
        page.Append("        <title>").Append(encodedMessage).Append("</title>\r\n");
        page.Append("        <meta name=\"viewport\" content=\"width=device-width\" />\r\n");
        page.Append("        <style>\r\n");
        page.Append("         body {font-family:\"Verdana\";font-weight:normal;font-size: .7em;color:black;} \r\n");
        page.Append("         p {font-family:\"Verdana\";font-weight:normal;color:black;margin-top: -5px}\r\n");
        page.Append("         b {font-family:\"Verdana\";font-weight:bold;color:black;margin-top: -5px}\r\n");
        page.Append("         H1 { font-family:\"Verdana\";font-weight:normal;font-size:18pt;color:red }\r\n");
        page.Append("         H2 { font-family:\"Verdana\";font-weight:normal;font-size:14pt;color:maroon }\r\n");
        page.Append("         pre {font-family:\"Consolas\",\"Lucida Console\",Monospace;font-size:11pt;margin:0;padding:0.5em;line-height:14pt}\r\n");
        page.Append("         .marker {font-weight: bold; color: black;text-decoration: none;}\r\n");
        page.Append("         .version {color: gray;}\r\n");
        page.Append("         .error {margin-bottom: 10px;}\r\n");
        page.Append("         .expandable { text-decoration:underline; font-weight:bold; color:navy; cursor:hand; }\r\n");
        page.Append("         @media screen and (max-width: 639px) {\r\n");
        page.Append("          pre { width: 440px; overflow: auto; white-space: pre-wrap; word-wrap: break-word; }\r\n");
        page.Append("         }\r\n");
        page.Append("         @media screen and (max-width: 479px) {\r\n");
        page.Append("          pre { width: 280px; }\r\n");
        page.Append("         }\r\n");
        page.Append("        </style>\r\n");
        page.Append("    </head>\r\n\r\n");
        page.Append("    <body bgcolor=\"white\">\r\n\r\n");
        page.Append("            <span><H1>Server Error in '/' Application.<hr width=100% size=1 color=silver></H1>\r\n\r\n");
        page.Append("            <h2> <i>").Append(encodedMessage).Append("</i> </h2></span>\r\n\r\n");
        page.Append("            <font face=\"Arial, Helvetica, Geneva, SunSans-Regular, sans-serif \">\r\n\r\n");
        page.Append("            <b> Description: </b>An unhandled exception occurred during the execution of the current web request. Please review the stack trace for more information about the error and where it originated in the code. <br><br>\r\n\r\n");
        page.Append("            <b> Exception Details: </b>").Append(encodedType).Append(": ").Append(encodedMessage).Append("<br><br>\r\n\r\n");
        page.Append("            <b>Source Error:</b> <br><br>\r\n\r\n");
        page.Append("            <table width=100% bgcolor=\"#ffffcc\">\r\n");
        page.Append("               <tr>\r\n");
        page.Append("                  <td>\r\n");
        page.Append("                      <code><pre>\r\n\r\n").Append(encodedSnippet).Append("</pre></code>\r\n\r\n");
        page.Append("                  </td>\r\n");
        page.Append("               </tr>\r\n");
        page.Append("            </table>\r\n\r\n");
        page.Append("            <br>\r\n\r\n");
        page.Append("            <b>Source File:</b> ").Append(encodedFile);
        page.Append("&nbsp;&nbsp;&nbsp;&nbsp;<b>Line:</b> ").Append(sourceLine.ToString()).Append("<br><br>\r\n\r\n");
        page.Append("            <b>Stack Trace:</b> <br><br>\r\n\r\n");
        page.Append("            <table width=100% bgcolor=\"#ffffcc\">\r\n");
        page.Append("               <tr>\r\n");
        page.Append("                  <td>\r\n");
        page.Append("                      <code><pre>\r\n\r\n").Append(encodedTrace).Append("</pre></code>\r\n\r\n");
        page.Append("                  </td>\r\n");
        page.Append("               </tr>\r\n");
        page.Append("            </table>\r\n\r\n");
        page.Append("            <br>\r\n\r\n");
        page.Append("            <hr width=100% size=1 color=silver>\r\n\r\n");
        page.Append("            <b>Version Information:</b>&nbsp;Microsoft .NET Framework Version:4.0.30319; ASP.NET Version:4.8.4494.0\r\n\r\n");
        page.Append("            </font>\r\n\r\n");
        page.Append("    </body>\r\n");
        page.Append("</html>\r\n");
        page.Append("<!--\r\n");
        page.Append("[").Append(ex.Type.Substring(ex.Type.LastIndexOf('.') + 1)).Append("]: ").Append(ex.Message).Append("\r\n");
        page.Append("-->\r\n");
        return page.ToString();
    }

    /// <summary>
    /// Assembles a stack trace. The top line is the exception header, followed by a
    /// deepest-first sequence of frames. Framework frames end in an IL offset
    /// (+NNN); application frames end in a source file and line. None of it maps to
    /// real code.
    /// </summary>
    private string BuildStackTrace(string exceptionType, string exceptionMessage)
    {
        var sb = new StringBuilder(2048);
        sb.Append('[').Append(exceptionType.Substring(exceptionType.LastIndexOf('.') + 1))
          .Append(": ").Append(exceptionMessage).Append("]\r\n");

        var frameCount = _rng.Next(9, 18);
        for (var i = 0; i < frameCount; i++)
        {
            sb.Append("   ").Append(BuildFrame(i < frameCount / 3)).Append("\r\n");
        }

        return sb.ToString();
    }

    /// <summary>
    /// Builds one frame line. Application frames (the shallow third of the trace)
    /// carry a source file and line; deep framework frames carry an IL offset.
    /// </summary>
    private string BuildFrame(bool preferApplicationFrame)
    {
        var ns = Namespaces[_rng.Next(Namespaces.Length)];
        var cls = Classes[_rng.Next(Classes.Length)];
        var method = Methods[_rng.Next(Methods.Length)];
        var parameters = Parameters[_rng.Next(Parameters.Length)];

        var signature = ns + "." + cls + "." + method + "(" + parameters + ")";

        var isApplicationFrame = preferApplicationFrame || ns.StartsWith("Contoso", StringComparison.Ordinal);
        if (isApplicationFrame && _rng.Next(2) == 0)
        {
            var file = SourceFiles[_rng.Next(SourceFiles.Length)];
            var line = _rng.Next(11, 512);
            return signature + " in " + file + ":line " + line.ToString();
        }

        var offset = _rng.Next(12, 4096);
        return signature + " +" + offset.ToString();
    }
}
