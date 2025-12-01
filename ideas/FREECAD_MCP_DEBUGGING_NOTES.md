# FreeCAD MCP Bridge - Debugging Notes and Enhancement Ideas

**Date:** December 1, 2024  
**Context:** Smart Trim v1.3.0 development session  
**Author:** Claude (Opus 4) with Brian White

## Session Summary

During a debugging session for the smart_trim generator, extensive use of the FreeCAD MCP bridge revealed several issues and opportunities for improvement.

---

## What Worked ✅

| Operation | Tool | Notes |
|-----------|------|-------|
| Connection check | `freecad:check_freecad_connection` | Correctly reported FreeCAD running |
| Echo test | `freecad:test_echo` | Returned message correctly |
| List objects | `freecad:view_control` | Returned full JSON of document objects |
| Fit view | `freecad:view_control` | Reported success |
| Python execution | `freecad:execute_python` | Code executed (but see issues below) |
| Object creation | `freecad:execute_python` | Created objects, spreadsheets in document |

---

## What Did NOT Work ❌

### 1. Python Return Values Not Captured (Critical)

Every `execute_python` call returned:
```json
{"success": true, "result": "Code executed successfully"}
```

Instead of returning the actual expression value.

**Examples that should have returned data:**
```python
1 + 1                        # Should return: 2
"hello"                      # Should return: "hello"  
{"key": "value"}             # Should return: {"key": "value"}
"\n".join(results)           # Should return: the joined string
json.dumps(result, indent=2) # Should return: JSON string
```

**Exception handling DID work** - errors were returned:
```json
{"success": true, "result": "Python execution error: name 'App' is not defined"}
```

This proves the return path works; expression values just aren't being captured.

### 2. Print Output Not Captured

```python
print("Hello")  # Produced no visible output in response
```

**Note:** In FreeCAD, `print()` output goes to the Report View panel. Capturing this would require either:
- Redirecting stdout during execution
- Hooking into FreeCAD's Console/Report View mechanism

These are different implementation approaches with different tradeoffs.

### 3. Screenshot Timeout

```json
{"success": true, "result": "Screenshot timeout - GUI thread may be busy"}
```

No way to adjust timeout or retry.

### 4. File I/O Across Environment Boundary

Writing to `/tmp/` from FreeCAD (on Mac) wasn't accessible from bash (in Claude's container). This is **expected behavior** - the MCP bridge connects two separate systems, and filesystem access doesn't cross that boundary.

---

## Root Cause Analysis

### Container/System Boundary Issues

- FreeCAD runs on the user's Mac
- Claude runs in a container in Anthropic's infrastructure  
- MCP bridge connects them via socket
- File I/O cannot cross this boundary (expected, not a bug)

### MCP Bridge Implementation Issues

The return value problem is purely a bridge implementation issue:
- Python code executes successfully in FreeCAD
- Errors ARE captured and returned
- Expression values are NOT captured and returned

**Hypothesis:** The bridge may be using `exec()` without capturing the result, rather than `eval()` or a mechanism that captures the last expression value (like IPython/Jupyter kernels do).

### What's NOT a Claude Limitation

None of the issues encountered were Claude limitations. With proper expression value return, all debugging could have been done interactively.

---

## Suggested Enhancements

### Priority 1: Fix Expression Value Return

This alone would solve ~80% of the usability issues. The bridge should return the value of the last expression, similar to IPython/Jupyter behavior.

**Test cases for verification:**
```python
1 + 1                    # Should return: 2
"hello"                  # Should return: "hello"
{"key": "value"}         # Should return: dict
[1, 2, 3]                # Should return: list
App.ActiveDocument.Name  # Should return: document name string
```

### Priority 2: Capture stdout/Report View (Optional)

Consider whether capturing print output is useful. Response could include separate fields:

```json
{
  "success": true,
  "result": "42",
  "stdout": "Debug: processing started\n",
  "stderr": ""
}
```

However, if expression values work properly, users would likely return data directly rather than printing it.

### Priority 3: Dedicated Analysis Tools

Common operations that currently require boilerplate Python code:

#### `freecad:get_object_info`
```json
{
  "name": "freecad:get_object_info",
  "parameters": {
    "object_name": "Extrude006",
    "properties": ["Label", "Shape.Faces[8].Area", "Shape.BoundBox"]
  }
}
```

#### `freecad:analyze_face`
```json
{
  "name": "freecad:analyze_face",
  "parameters": {
    "object_name": "Extrude006",
    "face_index": 8
  }
}
```

Returns: normal vector, edge count, bounding box, area, vertices, corner analysis, etc.

### Priority 4: Other Enhancements

#### Timeout parameter for screenshot
```json
{
  "name": "freecad:view_control",
  "parameters": {
    "operation": "screenshot",
    "timeout": 10
  }
}
```

#### Run macro by name
```json
{
  "name": "freecad:run_macro",
  "parameters": {
    "macro_name": "test_trim_v130.FCMacro"
  }
}
```

#### Rich selection info
```json
{
  "selected": [
    {
      "object": "Extrude006",
      "sub_elements": ["Face8"],
      "face_info": {
        "normal": [0, 1, 0],
        "area": 1177.1
      }
    }
  ]
}
```

---

## What NOT to Add

- Complex geometry creation tools - `execute_python` handles this fine once return values work
- Lots of specialized operations - fix the core issue first
- File transfer mechanisms - architectural boundary, work around with return values

---

## Workarounds Attempted (For Reference)

During the session, these workarounds were tried:

1. **Storing in App object:** `App.test_results = []` - code ran but couldn't retrieve
2. **Writing to spreadsheet cells:** Created spreadsheet, set values, couldn't read back
3. **Writing to file:** `/tmp/` not accessible across environment boundary  
4. **Global list + join:** Same issue, couldn't get final string out

None were successful due to the return value capture issue.

---

## Questions for Code Review

When examining the MCP bridge source:

1. How is Python code being executed? (`exec()` vs `eval()` vs `FreeCADGui.doCommand()`)
2. Is there result capture logic that's failing silently?
3. How are errors being captured? (This works, so the pattern exists)
4. Is stdout being redirected anywhere during execution?
5. What's the screenshot mechanism and why does it timeout?

---

## Summary

**One fix would transform usability:** Capturing and returning expression values from `execute_python`. Everything else is nice-to-have. The bridge architecture is sound (cross-system communication works), it's just missing this one critical feature.
