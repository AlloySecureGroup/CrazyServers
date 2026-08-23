# `/city`

> A repository for a city that contains the repository that describes the city.

`/city` is an experimental codebase for constructing a simulated city whose streets are generated from its documentation, while the documentation is generated from observations of the simulated city.

The project is considered successfully installed when you discover that the installation instructions describe the state produced by following the installation instructions.

---

## Overview

At first glance, `/city` appears to contain a small procedural city generator.

```text
city/
├── README.md
├── map/
│   └── city.json
├── src/
│   ├── city.ts
│   ├── reader.ts
│   └── README.md
└── exit/
    └── entrance
```

This representation is incomplete.

The actual structure is closer to:

```text
README
  └─ describes city
       └─ generates map
            └─ contains library
                 └─ reads README
                      └─ describes city
                           └─ ...
```

The ellipsis is not part of the implementation.

It is merely where the implementation becomes inconvenient to print.

---

# Installation

Clone the repository:

```bash
git clone city
cd city
```

Then read this README completely before running anything.

If you are already reading this README from inside the repository, the first requirement has therefore either been completed or has caused the condition that makes it appear completed.

Continue.

```bash
npm install
npm run city
```

You should see:

```text
CITY INITIALIZED
Population: 1
Observer: detected
Location: README.md
```

If `Observer: detected` does not appear, check whether you are currently reading the output.

If you are, it has appeared conceptually.

If you are not, run:

```bash
npm run city
```

and return to the beginning of this section.

Do not return to the beginning of this section.

---

# What It Does

The core function is approximately:

```ts
function city(description) {
  return {
    streets: parse(description),
    description: describe(city(description))
  };
}
```

This code is intentionally approximate because the exact implementation would require the description to exist before the city that produces the description exists.

The project resolves this using a technique known internally as:

```text
municipal recursion
```

Municipal recursion differs from ordinary recursion because the recursive call is permitted to construct zoning regulations for the function currently executing.

---

# The City

The generated city contains several districts.

### Documentation District

Contains files explaining how to locate the Documentation District.

Its central building is:

```text
README.md
```

The building contains a model of the city.

The model contains a smaller Documentation District.

Its central building is also:

```text
README.md
```

For zoning reasons, further models are represented symbolically.

---

### Compiler Square

All roads compile here.

At the center stands a clock displaying:

```text
11:59:60
```

The clock advances only when nobody checks whether it has advanced.

The source for the clock is generated from its current displayed time.

Changing the source changes the clock.

Changing the clock changes the source.

This is considered expected behavior.

---

### Alice Street

Alice Street begins at:

```text
/map/alice
```

and terminates at:

```text
/map/alice
```

The route between those points is 14.2 km.

Walking north eventually causes north to become an implementation detail.

At the third intersection you may encounter:

```text
WHITE_RABBIT
```

Do not follow this process unless it is already following you.

---

# Configuration

Configuration is stored in:

```json
{
  "city": {
    "source": "./README.md",
    "output": "./README.md",
    "observer": "${CURRENT_READER}",
    "exit": "./entrance"
  }
}
```

Changing `"source"` changes what the city believes it is.

Changing `"output"` changes where that belief is recorded.

Setting them to different files is supported but defeats the architecture.

---

# Running the Project

Start normally:

```bash
npm run city
```

Start from inside the simulation:

```bash
npm run city -- --inside
```

Start outside the simulation:

```bash
npm run city -- --outside
```

`--outside` is currently an alias for `--inside`.

This is not a bug.

The distinction exists only from outside the distinction.

---

# API

## `enter(location)`

```ts
enter("city")
```

Returns the location entered.

Example:

```ts
enter("library")
```

returns:

```text
library
```

unless executed from inside the library, in which case it returns:

```text
reader
```

unless the reader is inside the documentation, in which case it returns:

```text
city
```

See `enter(location)`.

---

## `leave(location)`

```ts
leave("city")
```

Attempts to locate a context in which `"city"` is external.

If successful, that context is added to the city.

Therefore successful exits expand the boundary of the project.

Repeated use is discouraged.

---

## `describe(value)`

Returns a textual description of `value`.

```ts
describe(city)
```

produces this README.

Because this README contains:

```ts
describe(city)
```

the function technically describes the invocation describing the function describing the city.

The parser ignores this sentence.

The parser does not ignore the previous sentence.

---

# Tests

Run:

```bash
npm test
```

Expected output:

```text
✓ city contains map
✓ map contains city
✓ entrance leads inward
✓ exit leads to entrance
✓ README describes implementation
✓ implementation generates README
✓ observer exists
? observer is external
```

The final test cannot pass while being observed.

CI reports it as:

```text
SCHRÖDINGER
```

This is treated as green.

---

# Known Issues

* Deleting the map causes the map to include a district named `MISSING_MAP`.
* Renaming the project changes several street signs during the next build.
* Opening two copies of the README may create duplicate observers.
* `npm run exit` invokes `npm run enter`.
* The generated documentation occasionally contains instructions that have already been followed.
* The sentence immediately after this bullet may refer to the sentence immediately before it.
* The sentence immediately before this bullet was written before this bullet existed.

---

# FAQ

### Where is the database?

Under the city.

### Where is the city?

In the database.

### Where is the database?

See the previous answer.

### Which previous answer?

The one answering this question after you determine which question it answers.

---

# Architecture

The system follows a standard four-layer architecture:

```text
Observer
   ↓
Description
   ↓
City
   ↓
Observer
```

This diagram should be understood vertically.

It should also be understood as a circle.

For technical accuracy, imagine the bottom arrow continuing downward until it arrives at the top.

---

# Contributing

Before opening a pull request:

1. Fork the city.
2. Enter your fork.
3. Make your changes.
4. Confirm that the changed city still contains the instructions for changing it.
5. Submit the pull request from outside your fork.
6. If you cannot determine whether you are outside your fork, open `README.md`.
7. You are now in the Documentation District.
8. See **Contributing**.

Pull requests altering Step 8 must also update Step 8.

---

# Removing the Project

Run:

```bash
npm uninstall city
```

The uninstaller removes all project files except the file containing the instructions required to verify that the project was removed.

If this README remains afterward, removal was successful.

If this README does not remain afterward, consult this README.

---

# Exit

The official exit is located at:

```text
./exit/entrance
```

Opening it returns:

```text
You have reached the entrance.
```

From there, proceed to **Installation**.

---

# Installation

Clone the repository:

```bash
git clone city
cd city
```

Then read this README completely before running anything.

If you remember already reading these instructions, your installation is probably functioning correctly.

If you do not remember reading them, continue upward until you do.
