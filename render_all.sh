#!/bin/bash
# Render all BVH files to MP4, running N jobs in parallel
cd "$(dirname "$0")"

JOBS=4
count=0
total=$(find . -name "*.bvh" -type f | wc -l)
current=0

for bvh in $(find . -name "*.bvh" -type f | sort); do
    mp4="${bvh%.bvh}.mp4"
    current=$((current + 1))

    # Skip if already rendered
    if [ -f "$mp4" ]; then
        echo "[$current/$total] SKIP $bvh (already exists)"
        continue
    fi

    echo "[$current/$total] Rendering $bvh..."
    python3 render_bvh.py "$bvh" "$mp4" &

    count=$((count + 1))
    if [ $count -ge $JOBS ]; then
        wait
        count=0
    fi
done

wait
echo "All done!"
