-- WTT UI, AGPL-3.0-only. KOReader v2026.07.1 reading modules stay unchanged.
-- Startup text uses the separately declared conditional branding derivative.
-- Ordinary KOReader ASAP deliberately never loads this UI or changes settings.
if os.getenv("WTT_READER_UI") ~= "1" then return { disabled = true } end

local WidgetContainer = require("ui/widget/container/widgetcontainer")
local ButtonDialog = require("ui/widget/buttondialog")
local Menu = require("ui/widget/menu")
local TouchMenu = require("ui/widget/touchmenu")
local CenterContainer = require("ui/widget/container/centercontainer")
local InfoMessage = require("ui/widget/infomessage")
local UIManager = require("ui/uimanager")
local Device = require("device")
local Event = require("ui/event")
local ReadHistory = require("readhistory")
local lfs = require("libs/libkoreader-lfs")
local Library = require("wttui/library")
local logger = require("logger")

local WTT = WidgetContainer:extend{ name = "wttui", is_doc_only = false }
local ROOT = "/mnt/us/WTT/Books"
local DOCUMENTS = "/mnt/us/documents"

local function findItem(items, id, seen, depth)
    seen, depth = seen or {}, depth or 0
    if not items or seen[items] or depth > 32 then return end
    seen[items] = true
    for _, item in ipairs(items or {}) do
        if item.id == id then return item end
        local found = findItem(item.sub_item_table or item, id, seen, depth + 1)
        if found then return found end
    end
end

function WTT:info(text)
    UIManager:show(InfoMessage:new{ text = text })
end

function WTT:init()
    self.ui.menu:registerToMainMenu(self)
    if self.ui.document then
        -- Override this instance only. Native menu remains available explicitly.
        self.native_tap = self.ui.menu.onTapShowMenu
        self.ui.menu.onTapShowMenu = function()
            return self:guard("toolbar", function() return self:showToolbar() end)
        end
        self.ui:registerPostReaderReadyCallback(function()
            self.ready = true
            self:guard("touch_registration", function() self:installToolbarZone() end)
        end)
    else
        self.ui:registerPostInitCallback(function()
            UIManager:nextTick(function()
                if not self.closed then self:guard("home", function() self:showHome(ROOT) end) end
            end)
        end)
    end
end

function WTT:installToolbarZone()
    self.ui:registerTouchZones{{
        id = "wtt_toolbar", ges = "tap",
        screen_zone = { ratio_x = 1/3, ratio_y = 1/3, ratio_w = 1/3, ratio_h = 1/3 },
        overrides = { "tap_forward", "tap_backward", "readermenu_tap", "readermenu_ext_tap" },
        handler = function()
            if self.failed then return self:showSafeControls() end
            return self:guard("toolbar", function() return self:showToolbar() end)
        end,
    }}
end

function WTT:guard(stage, action)
    if self.closed or self.failed then return true end
    local ok, result = pcall(action)
    if not ok then self:restoreNative(stage, result); return true end
    return result
end

function WTT:restoreNative(stage, err)
    if self.failed then return end
    self.failed = true
    -- Record only stage/code location, never arbitrary error text or document data.
    logger.err("WTT UI fallback", stage, tostring(err):match("([%w_/%.-]+%.lua:%d+)") or type(err))
    for _, close in ipairs({ self.closeDialog, self.closeSettings, self.closeHome }) do pcall(close, self) end
    if self.native_tap then self.ui.menu.onTapShowMenu = self.native_tap end
    if self.ui.unRegisterTouchZones then pcall(self.ui.unRegisterTouchZones, self.ui, {{ id = "wtt_toolbar" }}) end
    UIManager:nextTick(function()
        if self.closed then return end
        local ok = pcall(self.ui.menu.onShowMenu, self.ui.menu)
        if ok then
            pcall(self.info, self, "WTT 控制暂不可用，已切换原生菜单。\n请正常退出后通过 Skill 检查日志。")
        else
            logger.err("WTT native menu fallback failed")
            -- A failed sorter may already have consumed its menu table. Do not
            -- send the next tap back into that table, or claim fallback worked.
            self.ui.menu.onTapShowMenu = function() return self:showSafeControls() end
            self.ui.menu.onShowMenu = self.ui.menu.onTapShowMenu
            if self.ui.document then self:installToolbarZone() end
            self:showSafeControls()
        end
    end)
end

function WTT:showSafeControls()
    if self.closed then return true end
    self:closeDialog()
    -- These two callbacks deliberately bypass the failed WTT guard/menu sorter.
    local dialog = ButtonDialog:new{
        title = "WTT 设置暂不可用，原生菜单也未能打开。\n仍可继续阅读或退出；请通过 Skill 检查日志。",
        width_factor = 0.94,
        buttons = {{
            { text = "继续阅读", height = Device.screen:scaleBySize(60), callback = function() self:closeDialog() end },
            { text = "退出阅读", height = Device.screen:scaleBySize(60), callback = function() self:exitReader() end },
        }},
    }
    self.control_dialog = dialog
    UIManager:show(dialog)
    return true
end

function WTT:onSetDimensions()
    if self.ready and not self.failed then self:guard("resize", function() self:installToolbarZone() end) end
end

function WTT:onResume()
    if self.ready then
        UIManager:nextTick(function() self:guard("resume", function() self:installToolbarZone() end) end)
    end
end

function WTT:addToMainMenu(items)
    items.wtt_home = { text = "WTT 书架", sorting_hint = "main",
        callback = function()
            if self.ui.document then self.ui.menu:onTapCloseMenu()
            else self.ui.menu:onCloseFileManagerMenu() end
            if self.ui.document then self:returnHome() else self:showHome(ROOT) end
        end }
end

function WTT:closeHome()
    local home = self.home
    self.home = nil
    if home then UIManager:close(home) end
end

function WTT:openBook(file)
    if self.opening then return end
    if self.ui.document and self.ui.document.file == file then
        self:closeHome()
        return true
    end
    if lfs.attributes(file, "mode") ~= "file" then
        return self:info("书籍已移走，请刷新书架。")
    end
    self.opening = true
    -- This single upstream entry owns teardown, provider choice, sidecars and resume.
    local ok, err = pcall(function() require("apps/reader/readerui"):showReader(file) end)
    self.opening = false
    if not ok then error(err) end
end

function WTT:showHome(folder)
    if self.closed or self.failed then return end
    folder = folder or ROOT
    if folder ~= ROOT and folder ~= DOCUMENTS and not Library.inRoot(folder, ROOT)
            and not Library.inRoot(folder, DOCUMENTS) then folder = ROOT end
    self:closeHome()
    local loading = InfoMessage:new{ text = "正在读取书架…" }
    self.home = loading
    UIManager:show(loading)
    UIManager:nextTick(function()
        if not self.closed and self.home == loading then
            self:guard("library", function() self:populateHome(folder) end)
        end
    end)
end

function WTT:populateHome(folder)
    self:closeHome()
    local rows, entries = {}, {}
    local ok = pcall(function()
        local count = 0
        for name in lfs.dir(folder) do
            count = count + 1
            if count > 2002 then error("directory_limit") end
            entries[#entries + 1] = { name = name, mode = lfs.symlinkattributes(folder .. "/" .. name, "mode") }
        end
    end)
    if ok then
        local root = (folder == DOCUMENTS or Library.inRoot(folder, DOCUMENTS)) and DOCUMENTS or ROOT
        rows = Library.build(root, folder, G_reader_settings:readSetting("lastfile"),
            ReadHistory.hist, entries, function(file) return lfs.attributes(file, "mode") == "file" end,
            { ROOT, DOCUMENTS })
    else
        rows = {{ text = "目录读取失败或文件过多 · 请整理后刷新", select_enabled = false }}
    end
    if folder == ROOT then
        rows[#rows + 1] = { text = "历史书籍 · documents", folder = DOCUMENTS }
    elseif folder == DOCUMENTS then
        table.insert(rows, 1, { text = "返回 WTT 书架", folder = ROOT })
    end
    table.insert(rows, 1, { text = "微信读书 · 设置 · 刷新 · 退出", callback = function() self:showHomeActions(folder) end })
    local home = Menu:new{
        title = "WTT 书架", subtitle = folder == ROOT and "继续阅读与最近书籍"
            or (folder == DOCUMENTS and "历史书籍 · 保留原位置" or folder:match("([^/]+)$")),
        item_table = rows, width = Device.screen:getWidth(), height = Device.screen:getHeight(),
        covers_fullscreen = true, borderless = true, items_per_page = 9, items_font_size = 24,
        onMenuSelect = function(_, item)
            return self:guard("library_action", function()
                if item.select_enabled == false then return true end
                if item.file then self:openBook(item.file)
                elseif item.folder then self:showHome(item.folder)
                elseif item.callback then item.callback() end
                return true
            end)
        end,
        onClose = function() return self:guard("home_actions", function() self:showHomeActions(folder); return true end) end,
    }
    self.home = home
    UIManager:show(home)
end

function WTT:buttons(title, rows)
    self:closeDialog()
    local dialog
    for _, row in ipairs(rows) do
        for _, button in ipairs(row) do
            button.height = Device.screen:scaleBySize(60)
            button.font_size = 22
            local action = button.callback
            button.callback = function()
                return self:guard("control_action", function()
                    self:closeDialog()
                    if action then action() end
                end)
            end
        end
    end
    dialog = ButtonDialog:new{ title = title, buttons = rows, width_factor = 0.94 }
    self.control_dialog = dialog
    UIManager:show(dialog)
    return true
end

-- KOReader supplies self.dialog as the parent ReaderUI. Never close it here.
function WTT:closeDialog()
    local dialog = self.control_dialog
    self.control_dialog = nil
    if dialog then UIManager:close(dialog) end
end

function WTT:openWeRead()
    if self.ui.weread and self.ui.weread.openBookshelf then
        self.ui.weread:openBookshelf()
    else
        self:info("微信读书组件尚未加载，请通过 Skill 检查组件。")
    end
end

function WTT:showHomeActions(folder)
    self:buttons("WTT Reader", {
        {{ text = "微信读书", callback = function() self:openWeRead() end },
         { text = "设置", callback = function() self:showSettings() end }},
        {{ text = "刷新书架", callback = function() self:showHome(folder) end },
         { text = "USB / Wi-Fi 导书", callback = function()
             self:info("USB：退出阅读器后连接电脑，将书拖入 WTT/Books。\nWi-Fi：在设置中手动开启 SSH，电脑运行 WTT Skill 传书；日常传书不重置设备。")
         end }},
        {{ text = "返回书架" }, { text = "退出阅读", callback = function() self:exitReader() end }},
    })
end

function WTT:event(name)
    logger.info("WTT action", name)
    return self.ui:handleEvent(Event:new(name))
end

function WTT:showFormatControls()
    local config = self.ui.config
    if not config or not config.onShowConfigMenu then error("wttui/main.lua: format_controls_missing") end
    logger.info("WTT action", "format_controls")
    config:onShowConfigMenu()
    if not config.config_dialog then error("wttui/main.lua: format_dialog_missing") end
end

function WTT:showToolbar()
    if not self.ui.document or self.closed then return true end
    -- Stop selection like upstream ReaderMenu does, without opening bottom controls.
    self.ui.keyselection:stopHighlightIndicator(true)
    local paged = self.ui.paging ~= nil
    return self:buttons("阅读控制", {
        {{ text = "返回书架", callback = function() self:returnHome() end }, { text = "继续阅读" }},
        {{ text = paged and "PDF / 页面控制" or "字体与排版", callback = function() self:showFormatControls() end },
         { text = "目录", callback = function() self:event("ShowToc") end }},
        {{ text = "书签与标注", callback = function() self:event("ShowBookmark") end },
         { text = "搜索", callback = function() self:event("ShowFulltextSearchInput") end }},
        {{ text = "阅读设置", callback = function() self:showSettings() end },
         { text = "添加 / 取消书签", callback = function() self:event("ToggleBookmark") end }},
    })
end

function WTT:showSettings()
    local menu = self.ui.menu
    if not menu.tab_item_table then menu:setUpdateItemTable() end
    local sections = self.ui.document and {
        { "typeset", "字体、排版与 PDF" }, { "taps_and_gestures", "手势与翻页" },
        { "navi", "目录、书签与标注" }, { "search", "搜索与跳转" },
        { "screen", "屏幕与刷新" }, { "device", "设备与灯光" }, { "network", "Wi-Fi 与 SSH 传书" },
    } or { { "screen", "屏幕与刷新" }, { "device", "设备与灯光" }, { "network", "Wi-Fi 与 SSH 传书" } }
    local tab = { icon = "appbar.settings" }
    for _, section in ipairs(sections) do
        local native = findItem(menu.tab_item_table, section[1])
        if native then
            local children = native.sub_item_table or native
            tab[#tab + 1] = { text = section[2], sub_item_table = children }
        end
    end
    tab[#tab + 1] = { text = "微信读书", callback = function() self:closeSettings(); self:openWeRead() end }
    tab[#tab + 1] = { text = "关于 WTT", callback = function()
        self:info("WTT Reader 0.2.4\n阅读核心：KOReader v2026.07.1（KOReader contributors）\n微信插件：finlater/weread.koplugin v1.6.0\n源码：github.com/koreader/koreader；github.com/finlater/weread.koplugin\nWTT 界面与 KOReader 按 AGPLv3 提供源码与署名。\n长按正文可划线或记笔记；原 WTT 旧标注保留，尚未迁移。")
    end }
    tab[#tab + 1] = { text = "兼容菜单", callback = function() self:closeSettings(); menu:onShowMenu() end }
    self:closeSettings()
    local container = CenterContainer:new{ dimen = Device.screen:getSize(), ignore = "height" }
    container[1] = TouchMenu:new{ width = Device.screen:getWidth(), tab_item_table = { tab },
        show_parent = container, close_callback = function() self:closeSettings() end }
    self.settings_dialog = container
    UIManager:show(container)
end

function WTT:closeSettings()
    local dialog = self.settings_dialog
    self.settings_dialog = nil
    if dialog then UIManager:close(dialog) end
end

function WTT:returnHome()
    self:closeDialog()
    self:closeSettings()
    self.ui.menu:onTapCloseMenu()
    -- Keep the native document alive below the library; upstream owns book switching.
    logger.info("WTT action", "return_library")
    self:showHome(ROOT)
end

function WTT:exitReader()
    self:closeDialog()
    self:closeSettings()
    self:closeHome()
    -- Upstream owns lifecycle and Kindle framework restoration.
    self.ui:onClose()
end

function WTT:onCloseWidget()
    self.closed = true
    for _, close in ipairs({ self.closeDialog, self.closeSettings, self.closeHome }) do
        local ok = pcall(close, self)
        if not ok then logger.err("WTT close failed") end
    end
end

return WTT
