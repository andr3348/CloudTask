# Cloud Task API

REST API for managing tasks.

## Base URL

```
http://localhost:<PORT>/api
```

Default port is `3000` unless `PORT` is set (dev uses `3001`).

## Conventions

- All request/response bodies are JSON (`Content-Type: application/json`).
- Path params must be integers — `/api/tasks/abc` returns `400`.
- Unknown body properties are rejected with `400`.

### Enums

| Field      | Values                                |
| ---------- | ------------------------------------- |
| `status`   | `PENDING`, `IN_PROGRESS`, `COMPLETED` |
| `priority` | `LOW`, `MEDIUM`, `HIGH`               |

### Errors

| Status | Cause                                                                                                   |
| ------ | ------------------------------------------------------------------------------------------------------- |
| `400`  | Validation failed (invalid types, bad enum values, malformed dates, unknown properties, non-integer id) |
| `404`  | Task with the given id does not exist                                                                   |
| `500`  | Unexpected server error                                                                                 |

Validation errors return the failing constraints:

```json
{
  "statusCode": 400,
  "message": [
    "status must be one of the following values: PENDING, IN_PROGRESS, COMPLETED"
  ],
  "error": "Bad Request"
}
```

---

## Health check

### `GET /api`

Returns a greeting.

**Response** `200`

```json
"Hello World!"
```

---

## Tasks

### Task object

```json
{
  "id": 1,
  "title": "SomeTask1",
  "description": "My first task",
  "status": "PENDING",
  "priority": "HIGH",
  "dueDate": "2026-09-01T12:00:00.000Z",
  "createdAt": "2026-08-22T20:00:00.000Z",
  "updatedAt": "2026-08-22T20:00:00.000Z"
}
```

Nullable fields: `description` and `dueDate` are `null` when not provided.

### `GET /api/tasks`

List all tasks.

**Response** `200`

```json
[
  {
    "id": 1,
    "title": "SomeTask1",
    "description": "My first task",
    "status": "PENDING",
    "priority": "HIGH",
    "dueDate": "2026-09-01T12:00:00.000Z"
  }
]
```

Returns `[]` when no tasks exist.

### `GET /api/tasks/:id`

Retrieve a single task by id.

**Response** `200` — Task object

**Errors**

- `404` — task not found

### `POST /api/tasks`

Create a task.

**Request body**

| Field         | Type                    | Required | Constraints                                    | Default   |
| ------------- | ----------------------- | -------- | ---------------------------------------------- | --------- |
| `title`       | string                  | yes      | non-empty                                      | —         |
| `description` | string \| null          | no       | max 500 chars                                  | `null`    |
| `status`      | enum                    | no       | see [Enums](#enums)                            | `PENDING` |
| `priority`    | enum                    | no       | see [Enums](#enums)                            | `MEDIUM`  |
| `dueDate`     | ISO date string \| null | no       | valid date (e.g. `"2026-09-01T12:00:00.000Z"`) | `null`    |

```bash
curl -X POST http://localhost:3001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SomeTask1",
    "description": "My first task",
    "status": "PENDING",
    "priority": "HIGH",
    "dueDate": "2026-09-01T12:00:00.000Z"
  }'
```

**Response** `201` — created Task object

**Errors**

- `400` — validation failed

### `PUT /api/tasks/:id`

Replace a task. This is a full replacement, not a partial update — send every field that defines the task's desired state.

> Omitted optional fields (`description`, `dueDate`) are reset to `null`.

**Request body**

| Field         | Type                    | Required | Constraints                           |
| ------------- | ----------------------- | -------- | ------------------------------------- |
| `title`       | string                  | yes      | non-empty                             |
| `description` | string \| null          | no       | max 500 chars; omitted/null clears it |
| `status`      | enum                    | yes      | see [Enums](#enums)                   |
| `priority`    | enum                    | yes      | see [Enums](#enums)                   |
| `dueDate`     | ISO date string \| null | no       | valid date; omitted/null clears it    |

```bash
curl -X PUT http://localhost:3001/api/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SomeTask1 edited",
    "description": "Updated description",
    "status": "IN_PROGRESS",
    "priority": "LOW",
    "dueDate": "2026-10-15T09:00:00.000Z"
  }'
```

**Response** `200` — updated Task object

**Errors**

- `400` — validation failed
- `404` — task not found

### `DELETE /api/tasks/:id`

Delete a task.

```bash
curl -X DELETE http://localhost:3001/api/tasks/1
```

**Response** `200` — empty body

**Errors**

- `404` — task not found
