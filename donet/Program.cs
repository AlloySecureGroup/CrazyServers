using DecoyServer;

var builder = WebApplication.CreateBuilder(args);

// Strip Kestrel's own server header so we can present an IIS identity instead.
builder.WebHost.ConfigureKestrel(options => options.AddServerHeader = false);

var app = builder.Build();

var generator = new FakeErrorGenerator();
var logger = app.Logger;

app.Run(async context =>
{
    var request = context.Request;

    // The whole point of a decoy: log every probe so the noise has intel value.
    // We record who poked us and what they were looking for, then hand back a lie.
    logger.LogInformation(
        "Probe from {RemoteIp} {Method} {Path}{Query} UA={UserAgent}",
        context.Connection.RemoteIpAddress,
        request.Method,
        request.Path.Value,
        request.QueryString.Value,
        request.Headers.UserAgent.ToString());

    // Pretend the server is doing real work before it falls over.
    await Task.Delay(Random.Shared.Next(40, 320));

    context.Response.StatusCode = StatusCodes.Status500InternalServerError;
    context.Response.ContentType = "text/html; charset=utf-8";

    // Wear an old IIS / ASP.NET Framework costume. These headers are what a
    // scanner fingerprints on, so they need to match the body's story.
    var headers = context.Response.Headers;
    headers["Server"] = "Microsoft-IIS/10.0";
    headers["X-Powered-By"] = "ASP.NET";
    headers["X-AspNet-Version"] = "4.0.30319";
    headers.CacheControl = "private";

    var html = generator.BuildPage(request.Path.Value ?? "/");
    await context.Response.WriteAsync(html);
});

// Default to a single port; override with ASPNETCORE_URLS or the --urls argument.
if (string.IsNullOrEmpty(builder.Configuration["urls"]) &&
    string.IsNullOrEmpty(Environment.GetEnvironmentVariable("ASPNETCORE_URLS")))
{
    app.Urls.Add("http://0.0.0.0:8080");
}

logger.LogInformation("Decoy server listening. Every request returns a fabricated ASP.NET error page.");
app.Run();
