# DecoyServer

A honeypot web server that answers **every** request with a fabricated ASP.NET
"Yellow Screen of Death". The stack traces are assembled at random from real
framework symbols mixed with fictional application symbols (`Contoso.*`), so they
look convincing to a scanner or a casual attacker but describe no real code path.
The goal is deception: make a prober believe they have found a genuine, slightly
crufty .NET Framework app, and let them waste time chasing traces that lead
nowhere while you log the interaction.

## What it does

- Returns HTTP 500 with a pixel-accurate classic YSOD body for any path or method.
- Rotates exception types, messages, source snippets, file paths, and a
  9-to-17-frame stack trace on every response, so no two pages match.
- Wears an IIS 10 / .NET Framework 4.0.30319 costume via `Server`, `X-Powered-By`,
  and `X-AspNet-Version` headers, matching the story the body tells.
- Adds a short randomized delay to imitate real request processing.
- Logs every probe (remote IP, method, path, query, user agent) to the console so
  the traffic has intelligence value.

## Run it

Requires the .NET 8 SDK.

```bash
cd DecoyServer
dotnet run
```

It listens on `http://0.0.0.0:8080` by default. Point a browser or `curl` at it:

```bash
curl -i http://localhost:8080/admin/login.aspx
```

Override the binding with the standard ASP.NET Core switches:

```bash
dotnet run --urls "http://0.0.0.0:9000"
# or
ASPNETCORE_URLS="http://0.0.0.0:9000" dotnet run
```

## Tuning

Everything the generator draws from lives in `FakeErrorGenerator.cs` as plain
arrays: exception types and messages, namespaces, class and method names,
parameter lists, source file paths, and source snippets. Add or edit entries to
match the persona you want to project (a specific framework version, a different
fake product name, and so on). The `+NNN` IL offsets, line numbers, and frame
counts are all randomized in `BuildStackTrace` / `BuildFrame`.

## Operating notes

This is a defensive deception tool. A few things worth keeping in mind before you
stand one up:

- Keep it isolated. It should have no access to anything real, so that even if
  someone treats it as a foothold there is nothing behind it.
- The log stream is the payoff. Ship those probe lines somewhere you actually
  watch (a SIEM, a file, wherever) rather than letting them scroll past.
- Project a fictional identity only. The bundled `Contoso.*` names are deliberate
  placeholders. Do not dress the decoy up as some real third party's product.
- Understand the rules that apply to you. Running deception infrastructure and
  logging visitor data can carry legal and policy obligations depending on where
  and how you deploy it. Check before you point it at the open internet.
