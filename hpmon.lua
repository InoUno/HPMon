chat = require('chat')
files = require('files')
packets = require('packets')

_addon = _addon or {}
_addon.name = 'HPMon'
_addon.author = 'InoUno'
_addon.version = '1.0.0'
_addon.command = 'hpmon'

-- Inspired by:
--  https://github.com/ibm2431/addons/blob/master/capture/hptrack.lua

hpmon = hpmon or {}

hpmon.mobs = {}

-----------------
-- Misc
-----------------

function hpmon.getDbStats(mob)
  if mob and mob.level and hpmon.db[mob.zone] and hpmon.db[mob.zone][mob.name] and hpmon.db[mob.zone][mob.name][mob.level] then
    return hpmon.db[mob.zone][mob.name][mob.level]
  end
  return {}
end

function hpmon.getMob(id)
  if not hpmon.mobs[id] then
    local mob = windower.ffxi.get_mob_by_id(id)
    if mob and mob.hpp > 0 and mob.is_npc and mob.spawn_type == 16 then
      local dbMob = hpmon.getDbStats(mob)
      local hpp = mob.hpp ~= 0 and mob.hpp or 100
      hpmon.mobs[id] = {
        id = id,
        name = mob.name,
        zone = windower.ffxi.get_info().zone,
        level = nil,
        startHPP = hpp,
        hpp = hpp,
        dmgTaken = 0,

        changes = {},
        pending = {},
        lastChange = 0,

        log = {},
        min = dbMob.min,
        max = dbMob.max,
      }
    end
  end

  return hpmon.mobs[id]
end

function hpmon.ensureLevel(mob)
  if (mob.level == nil or mob.level == '?') and not mob.requestedWidescan then
    -- Widescan to get level
    mob.requestedWidescan = true
    windower.add_to_chat(7, '[HPMon] Widescanning to get level')
    packets.inject(packets.new('outgoing', 0xF4, {['Flags'] = 1}))
  end
end


function hpmon.formatOutput(mob)
  local lvl = ''
  if mob.level and mob.level ~= 0 then
    lvl = string.format(' (lvl %s)', mob.level or '?')
  end

  local hp = mob.min
  if mob.min ~= mob.max then
    hp = string.format('%d-%d', mob.min, mob.max)
  end

  return string.format('[%d] %s%s: %s HP', mob.id, mob.name, lvl, hp or 'unknown')
end

function hpmon.updateDatabase(mob)
  if not mob or mob.max < mob.min then
    return
  end

  -- Ensure latest file DB is loaded before updating it
  hpmon.db = hpmon.loadDatabase(hpmon.outputDbPath)

  if not hpmon.db[mob.zone] then
    hpmon.db[mob.zone] = {}
  end

  if not hpmon.db[mob.zone][mob.name] then
    hpmon.db[mob.zone][mob.name] = {}
  end

  if not hpmon.db[mob.zone][mob.name][mob.level] then
    hpmon.db[mob.zone][mob.name][mob.level] = {}
  end

  local updated = false
  local dbStats = hpmon.getDbStats(mob)
  if dbStats.min == nil or dbStats.min < mob.min then
    dbStats.min = mob.min
    updated = true
  end

  if dbStats.max == nil or dbStats.max > mob.max then
    dbStats.max = mob.max
    updated = true
  end

  if updated then
    hpmon.saveDatabase(hpmon.outputDbPath, hpmon.db)
    hpmon.exportDatabaseCsv(hpmon.outputDbPath, hpmon.db)
  end
end

-----------------
-- Mob handlers
-----------------

-- Register damage done
function hpmon.registerDamage(id, dmg)
  if dmg == 0 then
    return
  end

  local mob = hpmon.getMob(id)
  if not mob then
    return
  end

  local time = os.clock()
  hpmon.ensureLevel(mob)

  local change = { dmg = dmg, time = time }
  table.insert(mob.changes, change)
  table.insert(mob.pending, change)

  mob.lastChange = time
  mob.dmgTaken = mob.dmgTaken + dmg
end


-- Register a HPP change
function hpmon.registerHPP(id, hpp)
  if hpp == 0 then
    return
  end

  local mob = hpmon.getMob(id)
  if not mob then
    return
  end

  local deltaHPP = mob.hpp - hpp
  if deltaHPP == 0 then
    return
  end

  hpmon.ensureLevel(mob)

  local time = os.clock()
  local change = { deltaHPP = deltaHPP, time = time }
  table.insert(mob.changes, change)
  table.insert(mob.pending, change)
  mob.lastChange = time
  mob.hpp = hpp
end



-- Handle mob death
function hpmon.handleDeath(mobId)
  local mob = hpmon.getMob(mobId)
  if not mob then
    return
  end

  mob.lastChange = os.clock()
  mob.dead = true
end

------------------
-- Calculations
------------------


function hpmon.calculate(mob)
  -- Clean up dead mob
  if mob.dead and os.clock() - mob.lastChange >= 2 then
    local output = hpmon.formatOutput(mob)
    windower.add_to_chat(7, '[HPMon] ' .. output)

    if mob.min and mob.max then
      hpmon.fileAppend(hpmon.outputCsv, string.format('%d,%d,%s,%s,%d,%d\n', mob.zone, mob.id, mob.name, mob.level or '?', mob.min, mob.max))
      hpmon.updateDatabase(mob)
    end

    hpmon.mobs[mob.id] = nil
    return
  end

   -- Check if there are changes, and that more than a certain amount of time has passed
  if #mob.pending < 2 or os.clock() - mob.lastChange < 0.5 or mob.hpp == 0 then
    return
  end
  mob.pending = {}

  if mob.hpp == 1 then
    -- Can't rely on 1% HP for calculations since the range is not a whole number (range is 0.001-1.999%)
    return
  end

  -- The range is different dependant on the mobs total HP.
  -- If it's less than 100, then the HPP is floored instead of ceiled.
  local dHPP = mob.startHPP - mob.hpp
  local min = math.ceil(mob.dmgTaken * 100 / dHPP)
  local max = math.floor(mob.dmgTaken * 100 / (dHPP - 0.99999))

  -- Useful debug log to add
  if hpmon.debug then
    windower.add_to_chat(7, string.format('[HPMon] Damage: %d, Start HPP: %d, HPP: %d, Min: %d, Max: %d', mob.dmgTaken, mob.startHPP, mob.hpp, min, max))
  end

  if mob.min ~= nil and max < mob.min or mob.max ~= nil and min > mob.max then
    windower.add_to_chat(7, string.format('[HPMon] Invalid calculation: Current: %d-%d, Aggregated: %d-%d', min, max, mob.min, mob.max))
  end

  if min > max then -- Unexpected case happened
    windower.add_to_chat(7, string.format('[HPMon] Unexpected range: Damage: %d, Start HPP: %d, HPP: %d, Min: %d, Max: %d', mob.dmgTaken, mob.startHPP, mob.hpp, min, max))
    local temp = min
    min = max
    max = temp
  end
  table.insert(mob.log, { min = min, max = max })

  local updated = false
  if mob.max == nil or mob.max > max then
    mob.max = max
    updated = true
  end

  if mob.min == nil or mob.min < min then
    mob.min = min
    updated = true
  end

  if updated then
    local hp = mob.min
    if mob.min ~= mob.max then
      hp = string.format('%d-%d', mob.min, mob.max)
    end
    windower.add_to_chat(7, string.format('[HPMon] %s has HP: %s', mob.name, hp))
  end
end


-----------------
-- Check level
-----------------
function hpmon.setLevel(id, level)
  local mob = hpmon.getMob(id)
  if mob ~= nil and (mob.level == nil or level ~= '?') then
    mob.level = level
  end
end


local check_stats = {
    { 0xAA, '\31\200(\31\130High Evasion, High Defense\31\200)'},
    { 0xAB, '\31\200(\31\130High Evasion\31\200)' },
    { 0xAC, '\31\200(\31\130High Evasion, Low Defense\31\200)' },
    { 0xAD, '\31\200(\31\130High Defense\31\200)' },
    { 0xAE, '' },
    { 0xAF, '\31\200(\31\130Low Defense\31\200)' },
    { 0xB0, '\31\200(\31\130Low Evasion, High Defense\31\200)' },
    { 0xB1, '\31\200(\31\130Low Evasion\31\200)' },
    { 0xB2, '\31\200(\31\130Low Evasion, Low Defense\31\200)' },
}

local check_results = {
    { 0x40, '\30\02too weak to be worthwhile' },
    { 0x41, '\30\02like incredibly easy prey' },
    { 0x42, '\30\02like easy prey' },
    { 0x43, '\30\102like a decent challenge' },
    { 0x44, '\30\08like an even match' },
    { 0x45, '\30\68tough' },
    { 0x46, '\30\76very tough' },
    { 0x47, '\30\76incredibly tough' }
}

function hpmon.handleCheckMessage(data)
  local packet = packets.parse('incoming', data)

  local windowerMob = windower.ffxi.get_mob_by_index(packet['Target Index'])
  if not windowerMob then
    return false
  end

  -- Verify that it's a check package
  local level = packet['Param 1']
  local subMessageId = packet['Param 2']
  local message = packet['Message']

  local checkResult = nil
  local stats = nil

  -- Obtain the check type and condition string..
  for _, resultEntry in pairs(check_results) do
    if resultEntry[1] == subMessageId then
      checkResult = resultEntry[2]
    end
  end

  for _, statsEntry in pairs(check_stats) do
    if statsEntry[1] == message then
      stats = statsEntry[2]
    end
  end



  if message == 0xF9 then

  elseif checkResult == nil or stats == nil then
    -- Was not a check message
    return false
  end

  -- Adjust underflow
  if level == 4294967295 then
    level = -1
  end

  if windowerMob then
    local mob = hpmon.getMob(windowerMob.id)
    if message == 0xF9 and level == 0 then
      mob.requestRecordedHP = true
      windower.add_to_chat(7, string.format('[HPMon] %s (%d) is impossible to gauge.', mob.name, mob.id))
      hpmon.ensureLevel(mob)
    else
      hpmon.setLevel(mob.id, level)
      windower.add_to_chat(7, string.format('[HPMon] %s (%d) is level %s', mob.name, mob.id, level))
      hpmon.printRecordedHP(mob)
    end
  end
end


function hpmon.printRecordedHP(mob)
  mob.requestRecordedHP = false

  if not mob or not mob.level or mob.level == '?' then
    return
  end

  if hpmon.db[mob.zone] and hpmon.db[mob.zone][mob.name] and hpmon.db[mob.zone][mob.name][mob.level] then
    local dbMob = hpmon.db[mob.zone][mob.name][mob.level]
    local hp = dbMob.min .. ''
    if dbMob.min ~= dbMob.max then
      hp = hp .. '-' .. dbMob.max
    end
    windower.add_to_chat(7, string.format('[HPMon] Recorded HP: %s', hp))
  end
end

--------------------
-- NPC update
--------------------

function hpmon.handleNpcUpdate(data)
  local packet = packets.parse('incoming', data)
  local mask = packet['Mask']
  if mask ~= 7 then -- no HPP given
    return
  end

  hpmon.registerHPP(packet['NPC'], packet['HP %'])
end


--------------------
-- Defeat update
--------------------

function hpmon.handleDefeatMessage(data)
  local packet = packets.parse('incoming', data)

  if packet['Message'] == 6 or packet['Message'] == 20 then -- Mob defeated or falls to the ground
    hpmon.handleDeath(packet['Target'])
  end
end



--------------------
-- Widescan result
--------------------

function hpmon.handleWidescan(data)
  local packet = packets.parse('incoming', data)
  local windowerMob = windower.ffxi.get_mob_by_index(packet['Index'])
  if not windowerMob then
    return
  end
  local mob = hpmon.getMob(windowerMob.id)
  if not mob then
    return
  end

  hpmon.setLevel(mob.id, packet['Level'])
  mob.requestedWidescan = false
  if mob.requestRecordedHP then
    windower.add_to_chat(7, string.format('[HPMon] %s (%d) is level %s', mob.name, mob.id, packet['Level']))
    hpmon.printRecordedHP(mob)
  end
end

--------------------
-- Action handler
--------------------

function hpmon.actionHandler(action)
  -- Defeated message
  if action.message == 6 then
    hpmon.processDeath(action['Target'])
    return
  end

  -- Check if it's an action we should examine
  if not hpmon.msg_types[action.category] then
    if hpmon.debug then
      -- Debug missing effect handler
      for _, target in pairs(action.targets) do
        for _, effect in pairs(target.actions) do
          windower.add_to_chat(7, '[HPMon] Skipped effect ' .. action.category .. ' / ' .. effect.message .. ' with ' .. effect.param)
        end
      end
    end
    return
  end

  -- Handle each target of the action
  local dmgById = {}
  for _, target in pairs(action.targets) do
    dmgById[target.id] = 0

    for i, effect in pairs(target.actions) do
      local msg = hpmon.msg_types[action.category][effect.message]
      if msg then
        if msg[2] ~= 0 then
          dmgById[target.id] = dmgById[target.id] + (effect.param * msg[2])
        end
      elseif hpmon.debug then
        -- Debug missing effect handler
        windower.add_to_chat(7, '[HPMon] Skipped effect ' .. action.category .. ' / ' .. effect.message .. ' with ' .. effect.param)
      end
    end
  end

  for mobId, dmg in pairs(dmgById) do
    hpmon.registerDamage(mobId, dmg)
  end
end


-------------------
-- Chunk handler
-------------------

function hpmon.chunkHandler(id, data, modified, injected, blocked)
  if id == 0x00E then -- NPC update
    hpmon.handleNpcUpdate(data)
  elseif id == 0x029 then -- Check
    hpmon.handleCheckMessage(data)
    hpmon.handleDefeatMessage(data)
  elseif id == 0x0F4 then -- Widescan
    hpmon.handleWidescan(data)
  end
end


hpmon.msg_types = {
  [1] = {
    [1] = {'Melee Attack', 1},
    [15] = {'(Miss) Melee Attack', 0},
    [67] = {'Melee Attack (Crit)', 1},

  },
  [2] = {
    [352] = {'Ranged Attack', 1},
    [353] = {'Ranged Attack (Crit)', 1},
    [354] = {'(Miss) Ranged Attack', 0},
    [576] = {'Ranged Attack (Squarely)', 1},
    [577] = {'Ranged Attack (Truestrike)', 1},
  },
  [3] = {
    [102] = {'JA (Recover)', -1},
    [103] = {'WS (Recover', -1},
    [135] = {'WS', 1},
    --[142] = {'WS (Stat Down)', 1},
    --[159] = {'WS (Status Recover)', -1},
    [185] = {'WS', 1},
    --[186] = {'WS (Stat Down)', 1},
    [187] = {'WS (HP Drain)', 1},
    [188] = {'(Miss) WS', 0},
    [189] = {'WS (No Effect)', 0},
    --[194] = {'WS (Status)', 1},
    [197] = {'WS (Resisted)', 1},
    --[224] = {'WS (Recover MP)', -1},
    --[225] = {'WS (MP Drain)', 1},
    --[226] = {'WS (TP Drain)', 1},
    [238] = {'WS (Recover)', -1},
    [263] = {'AOE (Recovery)', -1},
    [264] = {'AOE Damage', 1},
    [317] = {'JA Hit', 1},
    [318] = {'JA (Recover)', -1},
    [323] = {'JA (No Effect)', 0},
    [324] = {'(Miss) JA', 0},
    [379] = {'JA (Magic Burst)', 1},
    [539] = {'WS (Recover)', -1},
  },
  [4] = {
    [2] = {'Magic Damage', 1},
    [7] = {'Magic (Recovery)', -1},
    [227] = {'Magic (Drain)', 1},
    [252] = {'Magic (Burst)', 1},
    [262] = {'Magic (Burst)', 1},
    [263] = {'AOE (Recovery)', -1},
    [264] = {'AOE Damage', 1},
    [274] = {'Magic (Burst Drain)', 1},
    [648] = {'Meteor', 1},
    [650] = {'Meteor (Burst)', 1},
    [651] = {'Meteor (Recover)', -1},
  },
  [6] = {
    [110] = {'Ability Dmg', 1},
    [263] = {'AOE (Recovery)', -1},
    [264] = {'AOE Damage', 1},
  },
  [11] = {
    [185] = {'Trust WS', 1},
    [238] = {'Mob Healing', -1},
  },
  [13] = {
    [317] = {'Bloodpact: Rage', 1},
  }
}

hpmon.add_effect_types = {
  [3] = {
    [288] = {'SC: Light', 1},
    [289] = {'SC: Darkness', 1},
    [290] = {'SC: Gravitation', 1},
    [291] = {'SC: Fragmentation', 1},
    [292] = {'SC: Distortion', 1},
    [293] = {'SC: Fusion', 1},
    [294] = {'SC: Compression', 1},
    [295] = {'SC: Liquefaction', 1},
    [296] = {'SC: Induration', 1},
    [297] = {'SC: Reverberation', 1},
    [298] = {'SC: Transfixion', 1},
    [299] = {'SC: Scission', 1},
    [300] = {'SC: Detonation', 1},
    [301] = {'SC: Impaction', 1},
    [302] = {'SC: Cosmic Elucidation', 1},
    [767] = {'SC: Radiance', 1},
    [768] = {'SC: Umbra', 1},
  }
}


-----------------------
-- File utility
-----------------------

-- Handles opening, or creating, a file object. Returns it.
--------------------------------------------------
function hpmon.fileOpen(path)
  local file = {
    stream = files.new(path, true),
    locked = false,
    scheduled = false,
    buffer = ''
  }
  return file
end

-- Handles writing to a file (gently)
--------------------------------------------------
function hpmon.fileAppend(file, text)
  if not file.locked then
    file.buffer = file.buffer .. text
    if not file.scheduled then
      file.scheduled = true
      coroutine.schedule(function() hpmon.fileWrite(file) end, 0.5)
    end
  else
    coroutine.schedule(function() hpmon.fileAppend(file, text) end, 0.1)
  end
end

-- Writes to a file and empties the buffer
--------------------------------------------------
function hpmon.fileWrite(file)
  file.locked = true
  local to_write = file.buffer
  file.buffer = ''
  file.scheduled = false
  file.stream:append(to_write)
  file.locked = false
end


---------------------------------
-- Database loading and saving --
---------------------------------

function hpmon.formatValue(value)
  local formatted
  local valueType = type(value)
  if valueType == 'string' then
    formatted = '\'' .. string.gsub(value, '\'', '\\\'') .. '\''
  elseif value ~= nil then
    formatted = '' .. value
  end

  return formatted or 'nil'
end

function hpmon.formatKey(key)
  if type(key) == 'number' then
    key = string.format('[%d]', key)
  elseif type(key) == 'string' then
    key = string.format('[\'%s\']', string.gsub(key, '\'', '\\\''))
  end
  return key
end

function hpmon.formatLine(content, indent)
  return string.format('%s%s', string.rep(' ', indent * 2), content)
end

function hpmon.formatDatabaseEntry(key, entry, lines, indent)
  local lineStart = hpmon.formatLine(string.format('%s = ', hpmon.formatKey(key)), indent)
  if type(entry) ~= 'table' then
    lines[#lines+1] = lineStart ..  hpmon.formatValue(entry) .. ','
  else
    lines[#lines+1] = lineStart .. '{'
    hpmon.formatDatabaseTable(entry, lines, indent)
    lines[#lines+1] = hpmon.formatLine('},', indent)
  end
end

function hpmon.formatDatabaseTable(dbTable, lines, indent)
  if indent == nil then
    indent = 0
  end

  local keys = {}
  for key in pairs(dbTable) do
     keys[#keys+1] = key
  end
  table.sort(keys)

  for _, key in ipairs(keys) do
    hpmon.formatDatabaseEntry(key, dbTable[key], lines, indent+1)
  end
end

function hpmon.saveDatabase(path, db)
  local lines = { 'local db = {' }
  hpmon.formatDatabaseTable(db, lines)
  lines[#lines+1] = '}'
  lines[#lines+1] = 'return db\n'
  local file = files.new(path .. '.lua', true)
  file:write(table.concat(lines, '\n'))
end

function hpmon.loadDatabase(path)
  local db = {}
  local file = files.new(path .. '.lua', true)
  if file:exists(path) then
    package.loaded[path] = nil
    db = require(path)
  end
  return db
end


function hpmon.exportDatabaseCsv(path, db)
  local lines = {}
  for zone, mobs in pairs(db) do
    for name, lvls in pairs(mobs) do
        for lvl, hp in pairs(lvls) do
          lines[#lines+1] = table.concat({ name, zone, lvl, hp.min, hp.max, (hp.min + hp.max) / 2 }, ',')
        end
    end
  end
  local file = files.new(path .. '.csv', true)
  table.sort(lines)
  file:write('Name,Zone,Level,Min,Max,Mid\n' .. table.concat(lines, '\n'))
end

hpmon.outputCsv = hpmon.fileOpen('./data/hp.csv')

hpmon.outputDbPath = 'data/db'
hpmon.db = hpmon.loadDatabase(hpmon.outputDbPath)

-----------------------
-- Register handlers
-----------------------
windower.register_event('action', hpmon.actionHandler)
windower.register_event('incoming chunk', hpmon.chunkHandler)
windower.register_event('prerender', function()
  for _, mob in pairs(hpmon.mobs) do
    hpmon.calculate(mob)
    -- local dbStats = hpmon.getDbStats(mob)
    -- local status = dbStats.min == nil and '?'
    -- if dbStats.min == nil then
    --   status = '[-]'
    -- elseif dbStats.min ~= dbStats.max then
    --   status = '[~]'
    -- else
    --   status = '[✓]'
    -- end
    -- windower.set_mob_name(mob.id, string.format("%s%s", status, mob.name))
  end
end)

windower.register_event('addon command', function (command, ...)
	command = command and command:lower()
	if command == 'export' then
    hpmon.exportDatabaseCsv(hpmon.outputDbPath, hpmon.db)
  elseif command == 'debug' then
    hpmon.debug = not hpmon.debug
    print("[HPMon] Debug is now " .. (hpmon.debug and 'ON' or 'OFF'))
	end
end)
