--!nocheck
-- Read-only dump of the Studio data the stat-rework tools use. Run in Edit mode (command bar or
-- the Studio MCP's execute_luau). It changes nothing in the place.
--
-- It stores three JSON strings in _G:
--   _G.__dl_attach_dump  one JSON object per line per attachment class module under
--                        ServerStorage.attachment_data: {path, class, class_def, items=[...]}
--   _G.__dl_weapon_dump  one line per weapon under ReplicatedStorage.data.item.<category>:
--                        {category, name, defaults, presets, markers, firing, generalData}
--   _G.__dl_gg           one line per ServerStorage.resources.gun_game_setups module
-- Non-ASCII bytes are replaced with "?" so the strings can be read in fixed-size chunks.
--
-- Retrieval used on 2026-11-21: read each string in 95,000-byte slices with
--   return "#C01#" .. string.sub(_G.__dl_attach_dump, 1, 95000)   -- and so on
-- through the MCP (results over its size limit are saved to a file), strip the 5-character
-- tag, concatenate, and save as data/raw/attachment_data.json (a JSON list of the lines),
-- data/raw/weapon_data.json and data/raw/gun_game_setups.json.

local HS = game:GetService("HttpService")

local function san(v, d)
	d = d or 0
	if d > 40 then
		return "<deep>"
	end
	local tv = typeof(v)
	if tv == "table" then
		local o = {}
		local isarr = (#v > 0)
		for k, x in v do
			o[isarr and k or tostring(k)] = san(x, d + 1)
		end
		return o
	elseif tv == "number" or tv == "string" or tv == "boolean" then
		return v
	end
	return "<" .. tv .. ">"
end

local function ascii(s)
	return (string.gsub(s, "[\128-\255]", "?"))
end

-- attachments
do
	local mods = {}
	for _, f in game:GetService("ServerStorage").attachment_data:GetDescendants() do
		if f:IsA("ModuleScript") and f.Parent:IsA("Folder") then
			table.insert(mods, f)
		end
	end
	table.sort(mods, function(a, b)
		return a:GetFullName() < b:GetFullName()
	end)
	local lines = {}
	for _, f in mods do
		local okc, ct = pcall(require, f)
		local entry = { path = f:GetFullName(), class = f.Name, class_def = okc and san(ct) or "ERR", items = {} }
		for _, a in f:GetChildren() do
			if a:IsA("ModuleScript") then
				local ok, t = pcall(require, a)
				local kids = {}
				for _, k in a:GetChildren() do
					table.insert(kids, k.Name .. ":" .. k.ClassName)
				end
				local it = ok and san(t) or { err = true }
				it.__name = a.Name
				it.__children = kids
				table.insert(entry.items, it)
			end
		end
		table.insert(lines, HS:JSONEncode(entry))
	end
	_G.__dl_attach_dump = ascii(table.concat(lines, "\n"))
end

-- weapons
do
	local items = game:GetService("ReplicatedStorage").data.item
	local lines = {}
	for _, cat in { "pistol", "rifle", "shotgun", "smg", "turret", "bolt_action", "launcher" } do
		for _, w in items[cat]:GetChildren() do
			local e = { category = cat, name = w.Name, presets = {} }
			local ok, d = pcall(require, w.defaults)
			e.defaults = ok and san(d) or ("ERR " .. tostring(d))
			local okp, p = pcall(require, w.properties)
			if okp then
				local markers = {}
				local function walk(t, path, depth)
					if depth > 8 then
						return
					end
					for k, v in t do
						if type(v) == "table" then
							if v.__marker then
								table.insert(markers, {
									path = path .. "." .. tostring(k),
									tied_to = v.tied_to,
									min_value = san(v.min_value),
									max_value = san(v.max_value),
									min_stat = v.min_stat,
									max_stat = v.max_stat,
								})
							else
								walk(v, path .. "." .. tostring(k), depth + 1)
							end
						end
					end
				end
				walk(p, "", 0)
				e.markers = markers
				e.firing = san(p.firing and { rpm = p.firing.rpm, firemodes = p.firing.firemodes } or nil)
				e.generalData = san(p.generalData and {
					name = p.generalData.name,
					class = p.generalData.class,
					magazine_type = p.generalData.magazine_type,
					operation_type = p.generalData.operation_type,
				} or nil)
			end
			if w:FindFirstChild("presets") then
				for _, pr in w.presets:GetChildren() do
					if pr:IsA("ModuleScript") then
						local okr, r = pcall(require, pr)
						e.presets[pr.Name] = okr and san(r) or ("ERR " .. tostring(r))
					end
				end
			end
			table.insert(lines, HS:JSONEncode(e))
		end
	end
	_G.__dl_weapon_dump = ascii(table.concat(lines, "\n"))
end

-- official setups
do
	local g = game:GetService("ServerStorage").resources.gun_game_setups
	local lines = {}
	for _, m in g:GetChildren() do
		if m:IsA("ModuleScript") then
			local ok, r = pcall(require, m)
			table.insert(lines, HS:JSONEncode({ name = m.Name, data = ok and san(r) or ("ERR " .. tostring(r)) }))
		end
	end
	_G.__dl_gg = ascii(table.concat(lines, "\n"))
end

return #_G.__dl_attach_dump, #_G.__dl_weapon_dump, #_G.__dl_gg
