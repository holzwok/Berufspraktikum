class spot():
    def __init__(self, fileid, cellid, x, y, pixels, tot_intensity):
        self.fileid = fileid
        self.cellid = cellid
        self.x = x
        self.y = y
        self.pixels = pixels
        self.total_intensity = tot_intensity 
        
# FIXME: decide whether it is worth to object orient this 
# spotlist = [FileID, CellID, x, y, pixels, f.tot, f.sig, f.median, f.mad, n_RNA, time, FileID_old]

