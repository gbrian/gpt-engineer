from gpt_engineer.core.context import (
  AI_CODE_GENERATOR_PARSER
)

ai_validation_code_response = """
Based on the provided project structure and the requirements for find & replace instructions, here is a JSON instance that conforms to the specified schema. This instance includes hypothetical changes that might be needed in the project files located at `/shared/onwaytransfers.com/dev/owt/OWTMonitoring`.

```json
{
  "code_changes": [
    {
      "change_type": "update",
      "file_path": "/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js",
      "existing_content": "function createBooking(bookingData) {",
      "new_content": "async function createBooking(bookingData) {"
    },
    {
      "change_type": "update",
      "file_path": "/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js",
      "existing_content": "return response.data;",
      "new_content": "return response.data;\n    } catch (error) {\n        console.error('Error creating booking:', error);\n        throw error;\n    }"
    },
    {
      "change_type": "new",
      "file_path": "/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/utils/logger.js",
      "existing_content": "",
      "new_content": "const fs = require('fs');\nconst path = require('path');\n\nconst logFilePath = path.join(__dirname, 'logs', 'app.log');\n\nfunction logError(message) {\n    const timestamp = new Date().toISOString();\n    fs.appendFileSync(logFilePath, `${timestamp} - ERROR: ${message}\\n`);\n}\n\nmodule.exports = { logError };"
    },
    {
      "change_type": "update",
      "file_path": "/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js",
      "existing_content": "const axios = require('axios');",
      "new_content": "const axios = require('axios');\nconst { logError } = require('./utils/logger');"
    },
    {
      "change_type": "update",
      "file_path": "/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js",
      "existing_content": "console.error('Error creating booking:', error);",
      "new_content": "logError('Error creating booking: ' + error.message);"
    }
  ]
}
```

### Explanation of Changes

1. **Update BookingService.js**:
   - **Change Type**: `update`
   - **File Path**: `/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js`
   - **Existing Content**: The function signature for `createBooking` is changed to `async` to allow for asynchronous operations.
   - **New Content**: Added error handling to log errors when creating a booking.

2. **New Logger Utility**:
   - **Change Type**: `new`
   - **File Path**: `/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/utils/logger.js`
   - **Existing Content**: None (new file).
   - **New Content**: A simple logger utility that logs errors to a file.

3. **Update BookingService.js to Include Logger**:
   - **Change Type**: `update`
   - **File Path**: `/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js`
   - **Existing Content**: Import statement for `axios`.
   - **New Content**: Added import for the new logger utility.

4. **Update Error Logging in BookingService.js**:
   - **Change Type**: `update`
   - **File Path**: `/shared/onwaytransfers.com/dev/owt/OWTMonitoring/nodejs-service/src/BookingService.js`
   - **Existing Content**: Console error logging.
   - **New Content**: Replaced console error logging with the logger utility.

### Notes
- The changes are hypothetical and should be adjusted based on actual requirements and existing code.
- Ensure that the indentation is preserved in the new content to maintain code structure and readability.
- The file paths and content should be verified against the actual project files for accuracy. 
"""

def test_ai_validation_code():
    res = AI_CODE_GENERATOR_PARSER.invoke(ai_validation_code_response)
    assert len(res.code_changes) == 5
    assert [c.change_type for c in res.code_changes] == ["update","update","new","update","update"]