// Diagnostic observer, not the final mod. No ppmod, network, or model dependency.
// Runtime validation is pending. Run only after reading docs/PROBE.md.
local root = getroottable();
foreach (name in ["Entities", "GetMapName", "Time", "RandomInt"]) {
    if (!(name in root)) {
        printl("[GG_DIAG] Missing API: " + name);
        return;
    }
}
if ("GGProbe" in root) {
    printl("[GG_DIAG] Probe already installed in this script VM; reload the map to replace it.");
    return;
}

::GGProbe <- {
    active = true,
    hooked = false,
    sequence = 0,
    map = GetMapName(),
    run_id = format("p2-%d-%d", Time().tointeger(), RandomInt(1, 1000000000))
};

// Engine names are JSON-escaped; no model output is evaluated as script.
GGProbe.Quote <- function(text) {
    local out = "\"";
    for (local i = 0; i < text.len(); i++) {
        local c = text[i];
        if (c == 34) out += "\\\"";
        else if (c == 92) out += "\\\\";
        else if (c < 32) out += format("\\u%04x", c);
        else out += text.slice(i, i + 1);
    }
    return out + "\"";
};
GGProbe.Emit <- function(kind, powered) {
    if (!::GGProbe.active) return;
    ::GGProbe.sequence++;
    local value = powered == null ? "null" : (powered ? "true" : "false");
    local target = ::GGProbe.hooked ? "\"catcher_1\"" : "null";
    local hook = ::GGProbe.hooked ? "true" : "false";
    printl("[GG_EVENT] {\"schema_version\":1,\"origin\":\"engine\",\"event\":" +
        ::GGProbe.Quote(kind) + ",\"map\":" + ::GGProbe.Quote(::GGProbe.map) +
        ",\"run_id\":" + ::GGProbe.Quote(::GGProbe.run_id) +
        format(",\"seq\":%d,\"game_time\":%.3f", ::GGProbe.sequence, Time()) +
        ",\"data\":{\"target\":" + target + ",\"powered\":" + value +
        ",\"laser_hook\":" + hook + "}}");
};
GGProbe.Hint <- function() {
    ::GGProbe.Emit("hint_requested", null); // Requests only; no hint generator yet.
};
GGProbe.Stop <- function() {
    ::GGProbe.Emit("probe_stopped", null);
    ::GGProbe.active = false; // Existing callbacks become inert, not gameplay-blocking.
};

// These two map/entity/output combinations were observed in installed BSP data.
// A target named catcher_1 elsewhere is NOT automatically the same puzzle.
local supported = GGProbe.map == "sp_a2_laser_intro" || GGProbe.map == "sp_a2_laser_stairs";
if (supported) {
    local catcher = Entities.FindByName(null, "catcher_1");
    if (catcher != null && catcher.GetClassname() == "prop_laser_catcher") {
        try {
            catcher.ValidateScriptScope();
            local scope = catcher.GetScriptScope();
            if ("GGProbe_Powered" in scope || "GGProbe_Unpowered" in scope) {
                throw "Callback name conflict; no hooks installed";
            }
            scope.GGProbe_Powered <- function() {
                if ("GGProbe" in getroottable()) ::GGProbe.Emit("laser_powered", true);
            };
            scope.GGProbe_Unpowered <- function() {
                if ("GGProbe" in getroottable()) ::GGProbe.Emit("laser_unpowered", false);
            };
            catcher.ConnectOutput("OnPowered", "GGProbe_Powered");
            catcher.ConnectOutput("OnUnpowered", "GGProbe_Unpowered");
            GGProbe.hooked = true;
        } catch (err) {
            GGProbe.active = false;
            printl("[GG_DIAG] Hook failed; reload the map before retrying: " + err);
            return;
        }
    }
}
GGProbe.Emit("bridge_attached", null); // Not a map_loaded or player_spawned event.
if (!GGProbe.hooked) printl("[GG_DIAG] Handshake only; this map/target is not supported.");
