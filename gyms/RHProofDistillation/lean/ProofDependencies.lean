import Lean

/-!
Proof-expression dependency probe for Lean 4.
An edge means a constant occurs in an elaborated type or value expression.
This does not claim an indispensable or minimized mathematical dependency.
-/

namespace RHDepProbe

open Lean

def infoKind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

def allowed (prefixes : Array String) (name : Name) : Bool :=
  prefixes.isEmpty || prefixes.any (fun pref => name.toString.startsWith pref)

/-- A bounded BFS through kernel-elaborated direct constant references. -/
def emit (env : Environment) (roots : Array Name) (maxDepth maxNodes : Nat)
    (prefixes : Array String) : IO Unit := do
  let mut queue : Array (Name × Nat) := roots.map (fun n => (n, 0))
  let mut seen : NameHashSet := {}
  let mut idx := 0
  let mut count := 0
  let mut depthLimited := false
  while idx < queue.size && count < maxNodes do
    let (name, depth) := queue[idx]!
    idx := idx + 1
    if seen.contains name then
      continue
    seen := seen.insert name
    count := count + 1
    match env.find? name with
    | none =>
      let item := Json.mkObj [
        ("name", toJson name.toString),
        ("depth", toJson depth),
        ("kind", toJson ("missing" : String)),
        ("type_refs", toJson (#[] : Array String)),
        ("value_refs", toJson (#[] : Array String))]
      IO.println s!"RHDEP1\t{item.compress}"
    | some info =>
      let typeRefs := info.type.getUsedConstants
      -- The proof of a theorem is opaque by default: request its value.
      let valueRefs := match info.value? (allowOpaque := true) with
        | some value => value.getUsedConstants
        | none => #[]
      let item := Json.mkObj [
        ("name", toJson name.toString),
        ("depth", toJson depth),
        ("kind", toJson (infoKind info)),
        ("type_refs", toJson (typeRefs.map Name.toString)),
        ("value_refs", toJson (valueRefs.map Name.toString))]
      IO.println s!"RHDEP1\t{item.compress}"
      if depth < maxDepth then
        for dep in typeRefs ++ valueRefs do
          if allowed prefixes dep && !seen.contains dep then
            queue := queue.push (dep, depth + 1)
      else
        if (typeRefs ++ valueRefs).any (allowed prefixes) then
          depthLimited := true
  let endRecord := Json.mkObj [
    ("visited", toJson count),
    ("truncated", toJson (decide (idx < queue.size))),
    ("depth_limited", toJson depthLimited),
    ("queued", toJson queue.size),
    ("max_depth", toJson maxDepth),
    ("max_nodes", toJson maxNodes)]
  IO.println s!"RHDEPEND\t{endRecord.compress}"

end RHDepProbe
