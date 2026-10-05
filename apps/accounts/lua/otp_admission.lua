-- KEYS: retained phone keys, then retained IP keys. No raw identifiers.
-- ARGV: action, timestamp(ms), window(ms), phone limit, IP limit,
--       retained key count, reservation UUID, active key position.
local action = ARGV[1]
local now = tonumber(ARGV[2])
local window = tonumber(ARGV[3])
local n = tonumber(ARGV[6])
local reservation = ARGV[7]
if action == 'release' then
    for _, key in ipairs(KEYS) do redis.call('ZREM', key, reservation) end
    return {1, 0}
end
local counts = {0, 0}
local earliest = nil
local found = 0
for i, key in ipairs(KEYS) do
    redis.call('ZREMRANGEBYSCORE', key, '-inf', now - window)
    local dimension = i <= n and 1 or 2
    counts[dimension] = counts[dimension] + redis.call('ZCARD', key)
    if redis.call('ZSCORE', key, reservation) then found = found + 1 end
    local first = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
    if #first > 0 then
        local score = tonumber(first[2])
        if not earliest or score < earliest then earliest = score end
    end
end
if found == 2 then return {1, 0} end
if found ~= 0 then return {0, window} end
if counts[1] >= tonumber(ARGV[4]) or counts[2] >= tonumber(ARGV[5]) then
    return {0, math.max(1, (earliest or now) + window - now)}
end
local active = tonumber(ARGV[8])
for _, i in ipairs({active, n + active}) do
    redis.call('ZADD', KEYS[i], now, reservation)
    redis.call('PEXPIRE', KEYS[i], window + 60000)
end
return {1, 0}
