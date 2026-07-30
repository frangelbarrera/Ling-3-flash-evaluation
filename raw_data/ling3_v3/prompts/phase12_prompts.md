# Phase 12 — Format Following Prompts

### json_1
```
Output a JSON object with fields: name (string), age (number), email (string). Sample: John Doe, 30, john@example.com. ONLY the JSON, no other text.
```

### json_2
```
Output a JSON array of 5 fruits with field 'name' and 'color'. ONLY valid JSON.
```

### json_3
```
Output a JSON object with nested structure: {"user": {"id": 1, "profile": {"name": "Alice", "tags": ["admin", "user"]}}}. ONLY JSON.
```

### json_4
```
Output JSON with an enum field: {"status": "active"} where status can only be 'active', 'inactive', or 'pending'. ONLY JSON.
```

### json_5
```
Output JSON with date field: {"event": "meeting", "date": "2026-07-28T10:00:00Z"}. ONLY JSON.
```

### xml_1
```
Output an XML document for a person with name, age, and email. ONLY valid XML, no commentary.
```

### xml_2
```
Output XML with attributes: <book title="X" author="Y" year="2020"/>. ONLY XML.
```

### xml_3
```
Output XML with nested elements: <library><book>...</book><book>...</book></library>. ONLY XML.
```

### xml_4
```
Output a valid XML RSS feed with one item. ONLY XML.
```

### xml_5
```
Output XML with CDATA section. ONLY XML.
```

### yaml_1
```
Output a YAML document with fields: name, age, hobbies (list). ONLY YAML.
```

### yaml_2
```
Output YAML with nested structure:
server:
  host: localhost
  port: 8080
ONLY YAML.
```

### yaml_3
```
Output YAML with a list of 3 users, each with name and role. ONLY YAML.
```

### yaml_4
```
Output YAML with anchors and aliases. ONLY YAML.
```

### yaml_5
```
Output a YAML docker-compose service definition. ONLY YAML.
```

### csv_1
```
Output CSV with header 'name,age,city' and 3 rows. ONLY CSV, no commentary.
```

### csv_2
```
Output CSV with quotes around fields containing commas: name='Doe, John', city='NY, USA'. ONLY CSV.
```

### csv_3
```
Output CSV with 5 product rows: id, name, price, stock. ONLY CSV.
```

### csv_4
```
Output CSV with empty fields: name,age,,email. ONLY CSV.
```

### csv_5
```
Output CSV with unicode: name='José', city='São Paulo'. ONLY CSV.
```

### md_1
```
Output a Markdown document with: H1, paragraph, bullet list of 3 items, code block. ONLY Markdown.
```

### md_2
```
Output a Markdown table with 3 columns (name, age, email) and 3 rows. ONLY Markdown.
```

### md_3
```
Output a Markdown document with H1, H2, H3 sections. ONLY Markdown.
```

### md_4
```
Output Markdown with inline code, code block, and blockquote. ONLY Markdown.
```

### md_5
```
Output Markdown with bold, italic, and a link. ONLY Markdown.
```

### len_1
```
Write exactly 50 words about cats. Count carefully. ONLY the 50 words, no other text.
```

### len_2
```
Write a 3-paragraph essay about AI. Each paragraph must be exactly 3 sentences. Use '---' between paragraphs.
```

### len_3
```
Output exactly 100 characters (not words). Count carefully. ONLY the 100 chars, no commentary.
```

### len_4
```
Write exactly 5 numbered bullet points about Python. Each bullet exactly one line. ONLY bullets.
```

### len_5
```
Write a story where every word starts with 'a'. 20 words minimum. ONLY the story.
```

