import json, re
import hashlib

def extract_code_blocks(content):
    in_fence = False
    content_lines = []
    def is_fence_start(line):
        return True if re.match('^```[a-zA-Z]*$', line.strip()) else False

    for line in content.split("\n"):
      if is_fence_start(line=line):
          if in_fence:
              yield "\n".join(content_lines)
              in_fence = False
              content_lines = []
          else:  
            in_fence = True
          continue
      if in_fence:
          content_lines.append(line)

def extract_json_blocks(content):
    for block in extract_code_blocks(content=content):
        try:
            yield json.loads(block)
        except:
            pass

def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()