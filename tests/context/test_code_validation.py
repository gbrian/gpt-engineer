from gpt_engineer.core.context import (
  AI_CODE_GENERATOR_PARSER
)

def test_ai_validation_code():
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

    res = AI_CODE_GENERATOR_PARSER.invoke(ai_validation_code_response)
    assert len(res.code_changes) == 5
    assert [c.change_type for c in res.code_changes] == ["update","update","new","update","update"]


def test_ai_validation_code_2():
    response = """
    Sure, I'll provide the JSON instructions for the necessary code changes to implement the `Translations` API by extending `ApiBase`. This will include creating a new file for the `Translations` class and updating the `u343303174_tpalmContext` class to include the `Translations` entity.
      
      ### JSON Instructions
      
      ```json
      {
        "code_changes": [
          {
            "change_type": "new",
            "file_path": "/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Api/Translations.cs",
            "new_content": "using DegatecCore.Common.Database;\nusing Microsoft.EntityFrameworkCore;\nusing OWTWeb.OWTDB.Entities;\nusing System.Collections.Generic;\nusing System.Threading.Tasks;\n\nnamespace OWTWeb.OWTDB.Api\n{\n    public class Translations : ApiBase\n    {\n        public async Task<IList<Translation>> GetAllTranslationsAsync()\n        {\n            return await DbContext.Translations.ToListAsync();\n        }\n\n        public async Task<Translation> GetTranslationByIdAsync(ulong id)\n        {\n            return await DbContext.Translations.FindAsync(id);\n        }\n\n        public async Task AddTranslationAsync(Translation translation)\n        {\n            DbContext.Translations.Add(translation);\n            await DbContext.SaveChangesAsync();\n        }\n\n        public async Task UpdateTranslationAsync(Translation translation)\n        {\n            DbContext.Entry(translation).State = EntityState.Modified;\n            await DbContext.SaveChangesAsync();\n        }\n\n        public async Task DeleteTranslationAsync(ulong id)\n        {\n            var translation = await DbContext.Translations.FindAsync(id);\n            if (translation != null)\n            {\n                DbContext.Translations.Remove(translation);\n                await DbContext.SaveChangesAsync();\n            }\n        }\n    }\n}\n"
          },
          {
            "change_type": "update",
            "file_path": "/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Entities/u343303174_tpalmContext.cs",
            "existing_content": "public virtual DbSet<AppTranslation> AppTranslations { get; set; }",
            "new_content": "public virtual DbSet<AppTranslation> AppTranslations { get; set; }\npublic virtual DbSet<Translation> Translations { get; set; }"
          },
          {
            "change_type": "update",
            "file_path": "/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Entities/u343303174_tpalmContext.cs",
            "existing_content": "OnModelCreatingPartial(modelBuilder);",
            "new_content": "modelBuilder.Entity<Translation>(entity =>\n            {\n                entity.ToTable(\"app_translations\");\n\n                entity.HasKey(e => e.Id)\n                    .HasName(\"PRIMARY\");\n\n                entity.HasIndex(e => e.App)\n                    .HasDatabaseName(\"idx_app\");\n\n                entity.Property(e => e.Id)\n                    .HasColumnType(\"int(11)\")\n                    .HasColumnName(\"id\");\n\n                entity.Property(e => e.App)\n                    .IsRequired()\n                    .HasMaxLength(255)\n                    .HasColumnName(\"app\");\n\n                entity.Property(e => e.Key)\n                    .IsRequired()\n                    .HasMaxLength(255)\n                    .HasColumnName(\"key\");\n\n                entity.Property(e => e.Translation)\n                    .IsRequired()\n                    .HasColumnType(\"text\")\n                    .HasColumnName(\"translation\");\n\n                entity.Property(e => e.Language)\n                    .IsRequired()\n                    .HasMaxLength(2)\n                    .HasColumnName(\"language\");\n            });\n\n            OnModelCreatingPartial(modelBuilder);"
          }
        ]
      }
      ```
      
      ### Explanation of Changes
      
      1. **New File: `Translations.cs`**
         - **Path**: `/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Api/Translations.cs`
         - **Content**: Implements CRUD operations for the `Translation` entity by extending `ApiBase`.
      
      2. **Update `u343303174_tpalmContext.cs` to Include `Translations` DbSet**
         - **Path**: `/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Entities/u343303174_tpalmContext.cs`
         - **Existing Content**: `public virtual DbSet<AppTranslation> AppTranslations { get; set; }`
         - **New Content**: Adds `public virtual DbSet<Translation> Translations { get; set; }`
      
      3. **Update `u343303174_tpalmContext.cs` to Configure `Translation` Entity**
         - **Path**: `/shared/onwaytransfers.com/dev/owt/OWTDB/OWTDB/Entities/u343303174_tpalmContext.cs`
         - **Existing Content**: `OnModelCreatingPartial(modelBuilder);`
         - **New Content**: Adds configuration for the `Translation` entity before calling `OnModelCreatingPartial(modelBuilder);`
      
      These changes will add the necessary CRUD operations for managing translations by extending `ApiBase`, similar to how it's done for `Agencies`.
    """
    res = AI_CODE_GENERATOR_PARSER.invoke(response)
    assert len(res.code_changes) == 2
    assert [c.change_type for c in res.code_changes] == ["new","update","update"]
