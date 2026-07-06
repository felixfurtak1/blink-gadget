#!/bin/sh
echo "Content-type: text/html; charset=utf-8"
echo ""

echo "<html><head><title>Blink Gadget</title>"
echo "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
echo "<style>
* { box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    margin: 10px;
    padding: 0;
    background: #f5f5f5;
}
h1 { font-size: 1.5em; margin: 10px 0; }
h2, h3 { font-size: 1.2em; margin: 10px 0; }
.dir {
    background: #f0f0f0;
    padding: 8px 12px;
    margin: 4px 6px 4px 0;
    display: inline-block;
    border-radius: 5px;
}
.dir a {
    text-decoration: none;
    color: #0066cc;
    font-size: 1em;
}
.dir a:hover { text-decoration: underline; }
.img-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
    margin: 10px 0;
}
.img-item {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.img-item img {
    width: 100%;
    height: auto;
    max-height: 200px;
    object-fit: contain;
    border-radius: 4px;
}
.img-item small {
    display: block;
    margin-top: 5px;
    font-size: 0.7em;
    word-break: break-all;
    color: #666;
}
.breadcrumb {
    background: #e8e8e8;
    padding: 8px 10px;
    margin: 10px 0;
    border-radius: 5px;
    font-size: 0.9em;
    overflow-x: auto;
    white-space: nowrap;
}
.breadcrumb a {
    text-decoration: none;
    color: #0066cc;
}
.breadcrumb a:hover { text-decoration: underline; }
.nav-links {
    margin: 10px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.nav-links a {
    display: inline-block;
    padding: 8px 15px;
    background: #0066cc;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-size: 0.9em;
}
.nav-links a:hover {
    background: #0052a3;
}
.nav-links a:active {
    transform: scale(0.95);
}
p a {
    display: inline-block;
    padding: 8px 15px;
    background: #0066cc;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    font-size: 0.9em;
    margin: 5px 5px 5px 0;
}
p a:hover {
    background: #0052a3;
}
p a:active {
    transform: scale(0.95);
}
em {
    color: #888;
    font-style: italic;
}

/* Touch-friendly improvements */
.dir a, .nav-links a, p a {
    touch-action: manipulation;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* Mobile-specific adjustments */
@media (max-width: 600px) {
    body { margin: 5px; }
    h1 { font-size: 1.2em; }
    .img-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 8px;
    }
    .img-item img { max-height: 150px; }
    .dir {
        padding: 6px 10px;
        font-size: 0.9em;
        margin: 3px 4px 3px 0;
    }
    .breadcrumb {
        font-size: 0.8em;
        padding: 6px 8px;
    }
    .nav-links a, p a {
        padding: 10px 12px;
        font-size: 0.85em;
        min-height: 44px;
    }
    .img-item small { font-size: 0.65em; }
}

@media (max-width: 400px) {
    .img-grid {
        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
        gap: 5px;
    }
    .img-item { padding: 5px; }
    .img-item img { max-height: 120px; }
}
</style>"
echo "</head><body>"

# Get the current directory from query string
CURRENT_DIR="/srv/www/blink"
SHOW_RECENT=0

if [ -n "$QUERY_STRING" ]; then
    # Check if we want to show recent view
    if [ "$QUERY_STRING" = "recent" ]; then
        SHOW_RECENT=1
    else
        DIR_ARG="${QUERY_STRING#dir=}"
        if [ -n "$DIR_ARG" ]; then
            CURRENT_DIR="/srv/www/blink$DIR_ARG"
        fi
    fi
fi

# Sanitize - prevent directory traversal
case "$CURRENT_DIR" in
    /srv/www/blink/*)
        CURRENT_DIR=$(echo "$CURRENT_DIR" | sed 's|//*|/|g')
        ;;
    *)
        CURRENT_DIR="/srv/www/blink"
        ;;
esac

if [ ! -d "$CURRENT_DIR" ]; then
    CURRENT_DIR="/srv/www/blink"
fi

echo "<h1>📷 Blink Gadget</h1>"

# Navigation links
echo "<div class='nav-links'>"
echo "<a href='?dir='>📁 Browse</a>"
echo "<a href='?recent'>🕐 Recent</a>"
echo "</div>"

# Show 10 most recent view
if [ $SHOW_RECENT -eq 1 ]; then
    echo "<h2>Recent</h2>"
    echo "<div class='img-grid'>"

    ls -t /srv/www/blink/*/*/* 2>/dev/null | head -10 | while read img; do
        if [ -f "$img" ]; then
            filename=$(basename "$img")
            url="${img#/srv/www}"
            echo "<div class='img-item'>"
            echo "<a href='$url'><img src='$url' loading='lazy'></a>"
            #echo "<a href='$url' target='_blank'><img src='$url' loading='lazy'></a>"
            #echo "<small>$filename</small>"
            echo "</div>"
        fi
    done

    echo "</div>"
    echo "<p><a href='?dir='>← Back to Browse</a></p>"
    echo "</body></html>"
    exit 0
fi

# Breadcrumb navigation
echo "<div class='breadcrumb'>📂 <a href='?dir='>root</a>"

# Build breadcrumb by splitting path manually
CURRENT_DIR_NO_PREFIX="${CURRENT_DIR#/srv/www/blink}"
if [ -n "$CURRENT_DIR_NO_PREFIX" ] && [ "$CURRENT_DIR_NO_PREFIX" != "/" ]; then
    CURRENT_DIR_NO_PREFIX="${CURRENT_DIR_NO_PREFIX#/}"

    FULL_PATH=""
    OLD_IFS="$IFS"
    IFS='/'
    for part in $CURRENT_DIR_NO_PREFIX; do
        if [ -n "$part" ]; then
            if [ -z "$FULL_PATH" ]; then
                FULL_PATH="/$part"
            else
                FULL_PATH="$FULL_PATH/$part"
            fi
            echo " › <a href='?dir=$FULL_PATH'>$part</a>"
        fi
    done
    IFS="$OLD_IFS"
fi

echo "</div>"

# Show subdirectories sorted by most recent first
echo "<h3>📁 Subdirectories</h3>"

DIR_LIST=$(ls -dt "$CURRENT_DIR"/*/ 2>/dev/null)

if [ -z "$DIR_LIST" ]; then
    echo "<p><em>No subdirectories</em></p>"
else
    echo "$DIR_LIST" | while read dir; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            rel_path="${dir#/srv/www/blink}"
            rel_path="${rel_path%/}"
            echo "<div class='dir'><a href='?dir=$rel_path'>📁 $dirname/</a></div>"
        fi
    done
fi
echo "<br>"

# Show images in current directory (most recent first)
echo "<h3>🖼️ Images in $(basename "$CURRENT_DIR")</h3>"
echo "<div class='img-grid'>"

# Check if any images exist first
IMAGE_LIST=$(ls -t "$CURRENT_DIR"/*.jpg "$CURRENT_DIR"/*.jpeg "$CURRENT_DIR"/*.png "$CURRENT_DIR"/*.gif 2>/dev/null | head -20)

if [ -z "$IMAGE_LIST" ]; then
    echo "<p><em>No images in this directory</em></p>"
else
    echo "$IMAGE_LIST" | while read img; do
        if [ -f "$img" ]; then
            filename=$(basename "$img")
            url="${img#/srv/www}"
            echo "<div class='img-item'>"
            echo "<a href='$url'><img src='$url' loading='lazy'></a>"
            #echo "<a href='$url' target='_blank'><img src='$url' loading='lazy'></a>"
            #echo "<small>$filename</small>"
            echo "</div>"
        fi
    done
fi

echo "</div>"

# Navigation footer
echo "<p><a href='?dir='>📁 Back to root</a> <a href='?recent'>🕐 Recent</a></p>"
echo "</body></html>"
