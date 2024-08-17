import re

SINGLE_LINE_MENTION_START = "@codx:"
MULTI_LINE_MENTION_START = "<codx"
MULTI_LINE_MENTION_END = "</codx>"

SINGLE_LINE_MENTION_START_PROGRESS = "@codx-processing:"
MULTI_LINE_MENTION_START_PROGRESS = "<codx-processing"
MULTI_LINE_MENTION_END_PROGRESS = "</codx-processing>"

class MentionFlags():
    no_knowledge: bool = False
    model: str = None

class Mention():
    mention: str = None
    start_line: int = 0
    end_line: int = 0
    flags: MentionFlags = MentionFlags()

    def add_line(self, line):
      line = self.extract_flags(line)
      if not self.mention:
          self.mention = line
      else:
          self.mention = f"{self.mention}\n{line}"

    def extract_flags(self, line):
        flag_patterns = {}
        for flag_name, flag_value in vars(MentionFlags).items():
            if isinstance(flag_value, bool):
                flag_patterns[flag_name] = r'--' + flag_name.replace('_', '-')
            elif isinstance(flag_value, str):
                flag_patterns[flag_name] = r'--' + flag_name.replace('_', '-') + r'=([^ ]+)'

        for flag, pattern in flag_patterns.items():
            match = re.search(pattern, line)
            if match:
                if isinstance(getattr(self.flags, flag), bool):
                    setattr(self.flags, flag, True)
                elif isinstance(getattr(self.flags, flag), str):
                    setattr(self.flags, flag, match.group(1))

                line = re.sub(pattern, '', line).strip()

        return line

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