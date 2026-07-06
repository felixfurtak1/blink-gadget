#!/bin/sh
echo "Content-type: text/html"
echo ""
echo "<html><head><title>Blink Gadget</title></head><body>"
echo "<h1>10 Most Recent Events: $(date)</h1>"
ls /srv/www/images/blink/*/*/* -t 2>/dev/null | head -10 | while read img; do
  if [ -f "$img" ]; then
    filename=$(basename "$img")
    url="${img#/srv/www}"
    echo "<div style='margin:10px'><img src='$url'><br>$filename</div>"
  fi
done
echo "</body></html>"
