# work with multiple .cub files

for site in "Connecting_Ridge" 'Peak Near Shackleton''Malapert Massif'

# 'Connecting Ridge'=-172.318538, -102.226492, -89.835617, -89.068587
# 'Peak Near Shackleton'=107.267511, 141.525764, -89.142001, -88.383872
# 'Malapert Massif'=-5.673513, 5.073011, -86.20588, -85.497357

# findimageoverlaps
do 
SECONDS=0 
findimageoverlaps fromlist= ${site}_cubs.lis overlaplist= ${site}_cubs_overlaps.lis
echo "complete findimageoverlaps"

# csv
overlapstats fromlist= ${site}_cubs.lis overlaplist= ${site}_cubs_overlaps.lis DETAIL=FULL TO=${site}_cubs_overlap_stats.csv TABLETYPE=CSV

# tab
overlapstats fromlist= ${site}_cubs.lis overlaplist= ${site}_cubs_overlaps.lis DETAIL=FULL TO=${site}_cubs_overlap_stats.txt TABLETYPE=TAB
echo "complete overlapstats"
echo "complete overlap functions for $site site in $SECONDS seconds"

done