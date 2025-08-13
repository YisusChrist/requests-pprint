## v1.2.4 (2025-08-13)

### Feat

- improve request body parsing (#97)

### Fix

- don't modify req.headers object when adding host header
- error control when response can't be read (#95)
- add support for python 3.9

### Refactor

- move type imports under TYPE_CHECKING for better performance
- update `pprint_http_request` typing
- simplify duplicate logic to parsing request body

## v1.2.3 (2025-06-16)

## v1.2.2 (2025-04-06)

### Feat

- handle print of binary content in body, simplify content-type handling

## v1.2.1 (2024-11-18)

### Fix

- handle response body printing based on content-type (#66)

### Refactor

- simplify calculation of `http_version` in `pprint_http_response` function

## v1.2.0 (2024-11-17)

### Refactor

- separate code into new modules, group common formatting logic into functions

## v1.1.1 (2024-08-28)

### Fix

- remove args validation due to errors

### Refactor

- update relative import and comments

## v1.1.0 (2024-08-13)

### Feat

- add support for async requests from aiohttp
- add tests and more package files
- add package files

### Fix

- avoid printing None text, update Readme example

### Refactor

- extract code from init file
