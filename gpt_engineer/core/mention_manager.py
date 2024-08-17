
SINGLE_LINE_MENTION_START = "@codx:"
MULTI_LINE_MENTION_START = "<codx"
MULTI_LINE_MENTION_END = "</codx>"

SINGLE_LINE_MENTION_START_PROGRESS = "@codx-processing:"
MULTI_LINE_MENTION_START_PROGRESS = "<codx-processing"
MULTI_LINE_MENTION_END_PROGRESS = "</codx-processing>"

class Mention():
    mention: str
    start_line: int
    end_line: int
    respone: str
    flags: [str]

    def __init__(self, mention, start_line, end_line=None, respone=None):
        self.mention = mention
        self.start_line = start_line
        self.end_line = end_line
        self.respone = respone
        self.flags = []

    def add_line(self, line):
      if not self.mention:
          self.mention = line
      else:
          self.mention = f"{self.mention}\n{line}"

def extract_mentions(content):
    content_lines = content.split("\n")
    mentions = []
    mention = None

    for ix, line in enumerate(content_lines):
        if SINGLE_LINE_MENTION_START in line:
            mention = Mention()
            mention.start_line = ix
            mention.add_line(line.split(SINGLE_LINE_MENTION_START)[1])
            mentions.append(mention)
            mention = None
    
        elif MULTI_LINE_MENTION_START in line:
            mention = Mention()
            mention.start_line = ix
            mentions.append(mention)
    
        elif MULTI_LINE_MENTION_END in line:
            mention.end_line = ix
            mention = None
    
        elif mention:
            mention.add_line(line)
    return mentions

def notify_mentions_in_progress(content):
    return content.replace(SINGLE_LINE_MENTION_START, SINGLE_LINE_MENTION_START_PROGRESS) \
              .replace(MULTI_LINE_MENTION_START, MULTI_LINE_MENTION_START_PROGRESS) \
              .replace(MULTI_LINE_MENTION_END, MULTI_LINE_MENTION_END_PROGRESS)

def notify_mentions_error(content, error):
    return content.replace("codx-processing", f"codx-error: {error}")  


def strip_mentions(content, mentions):
    content_lines = content.split("\n")
    new_content = []
    last_index = 0
    for mention in mentions:
        new_content = new_content + content_lines[last_index:mention.start_line]
        last_index = (mention.end_line if mention.end_line else mention.start_line) + 1
    if last_index < len(content) - 1:
        new_content = new_content + content_lines[last_index:]
    return "\n".join(new_content)

def replace_mentions(content, mentions):
    content_lines = content.split("\n")
    new_content = []
    last_index = 0
    for mention in mentions:
        new_content = new_content + content_lines[last_index:mention.start_line]
        new_content = new_content + mention.diff().split("\n")
        last_index = (mention.end_line if mention.end_line else mention.start_line) + 1
    if last_index < len(content) - 1:
        new_content = new_content + content_lines[last_index:]
    return "\n".join(new_content)