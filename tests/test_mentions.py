

from gpt_engineer.core.mention_manager import (
    Mention,
    extract_mentions,
    replace_mentions,
    SINGLE_LINE_MENTION_START,
    MULTI_LINE_MENTION_START,
    MULTI_LINE_MENTION_END
)

def test_single_single_mentions():
    content = f'''
    Some extra
    {SINGLE_LINE_MENTION_START} This is a mention
    more
    '''
    mentions = extract_mentions(content)
    assert len(mentions) == 1
    assert mentions[0].start_line == 2
    assert mentions[0].end_line == None
    assert mentions[0].mention == "This is a mention"

def test_single_multiple_mentions():
    content = f'''
    Some extra
    {MULTI_LINE_MENTION_START}
    This is a multi mention
    {MULTI_LINE_MENTION_END}
    more
    '''
    mentions = extract_mentions(content)
    assert len(mentions) == 1
    assert mentions[0].start_line == 3
    assert mentions[0].end_line == 3
    assert mentions[0].mention == "This is a multi mention"

def test_mix_single_multiple_mentions():
    content = f'''
    Some extra
    {SINGLE_LINE_MENTION_START} This is a mention
    more
    Some extra
    {MULTI_LINE_MENTION_START}
    This is a multi mention
    {MULTI_LINE_MENTION_END}
    more
    '''
    mentions = extract_mentions(content)

    assert len(mentions) == 2
    assert mentions[0].start_line == 2
    assert mentions[0].end_line == None
    assert mentions[0].mention == "This is a mention"

    assert mentions[1].start_line == 5
    assert mentions[1].end_line == 7
    assert mentions[1].mention == "This is a multi mention"

def test_replace_mentions():
    content = f'''
    Some extra
    {SINGLE_LINE_MENTION_START} This is a mention
    more
    Some extra
    {MULTI_LINE_MENTION_START}
    This is a multi mention
    more lines
    {MULTI_LINE_MENTION_END}
    more
    '''

    expected_content = '''
    Some extra
    REPLACE AT LINE 2
    more
    Some extra
    REPLACE AT LINE 6
    More lines
    linessss
    more
    '''
    mentions = extract_mentions(content)
    mentions[0].respone = "    REPLACE AT LINE 2"
    mentions[1].respone = "    REPLACE AT LINE 6\n    More lines\n    linessss"

    new_content = replace_mentions(content=content, mentions=mentions)

    assert new_content == expected_content