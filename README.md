# Crazy Fake Server

A zero-dependency Python fake server that produces:

- multilingual Unicode nonsense
- fake C#/.NET stack traces
- fake inner exceptions and HRESULTs
- fake async `MoveNext()` stack frames
- fake ASP.NET-style developer exception pages
- JSON error endpoints
- Zalgo, runes, emoji, cursed file paths, fake CLR diagnostics, and general reality failure

It is intended for local development, screenshots, UI testing, error-state demos, terminal chaos, and harmless joke environments.

> **Important:** this is not a real .NET or ASP.NET application. The diagnostics are fictional. The HTML page deliberately labels itself as fake.

## Requirements

Python 3.10+ is recommended.

No third-party packages are required.

## Start the server

```bash
python crazy_server.py
```

Default address:

```text
http://127.0.0.1:8000
```

The default `/` response is plain-text multilingual nonsense.

## ASP.NET-style mode

Use `--dotnet` to make `/`, `/stack`, and `/exception` render a fake ASP.NET-style developer exception page:

```bash
python crazy_server.py --dotnet
```

Then open:

```text
http://127.0.0.1:8000/
```

Every request generates a fresh fictional exception, stack, trace identifier, fake request diagnostics, and Unicode corruption.

## Maximum chaos

```bash
python crazy_server.py --dotnet --chaos 10
```

Chaos ranges from `1` to `10`.

Roughly:

- `1-3`: strange
- `4-6`: cursed
- `7-8`: CLR reality degradation
- `9-10`: Unicode catastrophe

## Custom port

```bash
python crazy_server.py --dotnet --port 5050
```

Then visit:

```text
http://127.0.0.1:5050/
```

## Custom status code

The generated error endpoints return HTTP 500 by default.

Change that with:

```bash
python crazy_server.py --dotnet --status 503
```

Or, naturally:

```bash
python crazy_server.py --dotnet --status 418
```

## Deterministic runs

Use a seed if you want generated output to be reproducible:

```bash
python crazy_server.py --dotnet --chaos 10 --seed 42
```

Requests still vary from one another, but the sequence is deterministic for the same seed and request order.

## Endpoints

### `/`

Main output.

Without `--dotnet`, returns a nonsense sentence.

With `--dotnet`, returns the fake ASP.NET-style exception page.

### `/health`

Always returns HTTP 200 with a small JSON health response:

```json
{
  "ok": true,
  "fake": true,
  "mode": "dotnet",
  "chaos": 10
}
```

### `/stack`

Returns a generated fake .NET stack trace.

With `--dotnet`, it renders as the fake developer exception page.

### `/exception`

Same general behavior as `/stack`.

### `/api/error`

Returns a fake ProblemDetails-ish JSON error response:

```json
{
  "title": "An absurd fake server error occurred.",
  "status": 500,
  "type": "System.PotatoSerializationException",
  "detail": "Object reference not set to an instance of a potato.",
  "traceId": "00-...",
  "hresult": "0xDEADBEEF",
  "stackTrace": "   at ...",
  "nonsense": "..."
}
```

### `/api/nonsense`

Returns generated nonsense as JSON.

One result:

```text
/api/nonsense
```

Twenty results:

```text
/api/nonsense?count=20
```

The maximum per request is 100.

### `/teapot`

Always returns HTTP `418`.

Obviously.

## Example curl commands

Plain error:

```bash
curl http://127.0.0.1:8000/stack
```

JSON error:

```bash
curl http://127.0.0.1:8000/api/error
```

Lots of nonsense:

```bash
curl "http://127.0.0.1:8000/api/nonsense?count=10"
```

Send a fake POST request to the ASP.NET-style page:

```bash
curl -i -X POST \
  -H "X-Correlation-ID: BANANA-𓆏-9001" \
  -H "Authorization: definitely-not-a-real-token" \
  "http://127.0.0.1:8000/exception?cheese=forbidden&moon=3"
```

The server does not execute the body or authenticate anything. It simply generates a response.

## All command-line options

```bash
python crazy_server.py --help
```

Options:

```text
--host HOST
    Bind address. Default: 127.0.0.1

--port PORT
    TCP port. Default: 8000

-c, --chaos N
    Chaos level from 1 to 10.

--dotnet
    Enable fake ASP.NET-style HTML error pages.

--status STATUS
    HTTP status for generated error endpoints.
    Default: 500.

--seed SEED
    Deterministic random seed.
```

## Binding to your LAN

By default the program binds only to loopback:

```text
127.0.0.1
```

That is the recommended mode.

If you intentionally want another device on your local network to reach it:

```bash
python crazy_server.py --host 0.0.0.0 --port 8000 --dotnet
```

The program will print a warning because it has no authentication and is designed as a fake development server, not a production web service.

Do not expose it directly to the public internet.

## What `--dotnet` changes

Normal mode:

```text
GET /
    -> plain Unicode nonsense

GET /stack
    -> fake .NET exception as text
```

With `--dotnet`:

```text
GET /
    -> HTML developer exception page

GET /stack
    -> HTML developer exception page

GET /exception
    -> HTML developer exception page
```

The page contains fictional versions of:

- exception type
- exception message
- stack frames
- async state-machine frames
- source file paths
- inner exceptions
- HRESULT
- ASP.NET Core-looking middleware frames
- trace identifier
- request method
- request path
- query parameters
- request headers
- fake CLR diagnostics
- Unicode nonsense

It is stylistically reminiscent of a development exception screen without copying a real framework page verbatim.

## Example fake output

```text
Unhandled exception. System.PotatoSerializationException:
Object reference not set to an instance of a potato.

   at Potato.Serialization.GrandmotherSerializer[TPotato].Deserialize(
       Potato potato, Int32 moonCount
   ) in C:\Reality\Production\Potato\Serialization\GrandmotherSerializer.cs:line 666

   at Goblin.Interop.OrbContext.<SummonGoblinAsync>d__13.MoveNext()
       in D:\build\agent\_work\13\s\Goblin\Interop\OrbContext.cs:line 420

 ---> System.NonEuclideanGeometryException:
 Sequence contains more than one moon.

   at NonEuclidean.Geometry.MoonController.ValidateReality(...)
   --- End of inner exception stack trace ---

HRESULT: 0xDEADBEEF
```

At chaos 10, expect substantially less cooperation from reality.

## Project structure

```text
crazy_fake_server/
├── crazy_server.py
└── README.md
```

## Stop the server

Press:

```text
Ctrl+C
```

## License

Do whatever you want with it for harmless development, demos, testing, and comedy.
