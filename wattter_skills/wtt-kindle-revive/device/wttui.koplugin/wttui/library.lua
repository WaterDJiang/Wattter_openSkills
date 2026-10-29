-- WTT UI, AGPL-3.0-only. Pure library model; KOReader owns document state.
local Library = {}
local formats = { epub = true, pdf = true, txt = true, mobi = true, azw3 = true }

function Library.isBook(path)
    local name = path:match("([^/]+)$") or ""
    return name:sub(1, 1) ~= "." and formats[(name:match("%.([^%.]+)$") or ""):lower()] == true
end

function Library.inRoot(path, root)
    return type(path) == "string" and path:sub(1, #root + 1) == root .. "/"
        and not path:find("/%.%./") and not path:find("/%.%./?$")
end

function Library.build(root, folder, last, history, entries, exists, book_roots)
    local rows, seen = {}, {}
    book_roots = book_roots or { root }
    local function addBook(file, label)
        local permitted = false
        for _, candidate in ipairs(book_roots) do
            if Library.inRoot(file, candidate) then permitted = true; break end
        end
        if seen[file] or not permitted or not Library.isBook(file) or not exists(file) then return false end
        seen[file] = true
        rows[#rows + 1] = { text = label .. (file:match("([^/]+)$") or file),
            file = file, kind = "book", select_enabled = true }
        return true
    end
    if folder == root then
        if last then addBook(last, "继续阅读 · ") end
        local n = 0
        for _, item in ipairs(history) do
            if exists(item.file) and addBook(item.file, "最近 · ") then n = n + 1 end
            if n >= 4 then break end
        end
    else
        rows[#rows + 1] = { text = "返回上级目录", kind = "folder",
            folder = folder:match("^(.*)/[^/]+$") }
    end
    table.sort(entries, function(a, b)
        if a.mode ~= b.mode then return a.mode == "directory" end
        return a.name:lower() < b.name:lower()
    end)
    for _, entry in ipairs(entries) do
        if entry.name:sub(1, 1) ~= "." then
            local file = folder .. "/" .. entry.name
            if entry.mode == "directory" and entry.name:sub(-4) ~= ".sdr" then
                rows[#rows + 1] = { text = entry.name .. "/", kind = "folder", folder = file }
            elseif entry.mode == "file" then
                addBook(file, "")
            end
        end
    end
    if #rows == 0 then
        rows[1] = { text = "还没有书 · 拖入 WTT/Books 后刷新", select_enabled = false, kind = "empty" }
    end
    return rows
end

return Library
