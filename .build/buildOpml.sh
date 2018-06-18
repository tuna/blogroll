#!/bin/bash

scriptpath=$(readlink "$0")
basedir=$(dirname $(dirname "$scriptpath"))

cd "$basedir"

# Extracting table from README.md
table=$(awk 'BEGIN {s=0};
               /^##/ {s=0};
               /^## List/ {s=1; next};
               /^\s*$/ {next};
               s {print}' ./README.md)

# Trim header
content=$(echo "$table" | tail -n +3)

# Generation
echo "
<opml version=\"2.0\">
  <head>
    <title>${OPML_TITLE}</title>
  </head>
  <body>
"

echo "$content" | while read -r line || [[ -n "$line" ]]; do
  name=$(echo $line | cut -f2 -d\| | sed 's/[ \t]*$//;s/^[ \t]*//')
  xml=$(echo $line | cut -f3 -d\| | sed 's/[ \t]*$//;s/^[ \t]*//')
  html=$(echo $line | cut -f4 -d\| | sed 's/[ \t]*$//;s/^[ \t]*//')
  echo "<outline title=\"$name\" xmlUrl=\"$xml\" htmlUrl=\"$html\"/>"
done

echo "
  </body>
</opml>
"
