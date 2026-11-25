export type Coordinate = { initial: number; literal: string; visibility: "public" | "hidden" };
export type Expression = Readonly<{
  op: string; type: "n" | "b"; literal?: string; key?: string; value?: boolean;
  args?: readonly Expression[];
}>;
export type Reaction = Readonly<{
  id: string; to: string; effects: readonly Readonly<{key: string; value: Expression}>[];
  desirability: Expression; gate: Expression;
}>;
export type Option = Readonly<{
  id: string; text: string; visible: Expression; performable: Expression; reactions: readonly Reaction[];
}>;
export type Page = Readonly<{
  id: string; lo: number; hi: number; gate: Expression; options: Readonly<Record<string,Option>>;
}>;
export type World = Readonly<{
  profile: "SWMD-SRG/1"; id: string; title: string; source: string; start: string;
  tie: "first" | "last"; coordinates: Readonly<Record<string,Coordinate>>; pages: Readonly<Record<string,Page>>;
}>;
export type State = { encounter: string; turn: number; values: Record<string,number> };
export type Observation = {
  world_id: string; encounter: string; turn: number; values: Record<string,number>;
  actions: {id: string; text: string}[]; status: "terminal" | "dead_end" | "decision";
};
export type Write = { key: string; before: number; after: number };
export type Branch = {
  id: string; status: "ok" | "blocked_destination"; next: State; writes: Write[]; squared_step_energy: number;
};
export type ActionAudit = {
  id: string; status: "ok" | "blocked_destination" | "no_eligible_reaction";
  scores: {id: string; eligible: boolean; score: number}[];
  winners: string[]; selected: string | null; branches: Branch[];
};
export type CounterfactualPacket = {
  profile: "SWMD-SRG/1"; world_id: string; pre: State; actions: ActionAudit[];
};
export function parseExpression(text: string, coordinates: Readonly<Record<string,unknown>>, expected?: "n"|"b"): Expression;
export function evaluate(node: Expression, state: Readonly<Record<string,number>>): number|boolean;
export function compileSWMD(source: string): World;
export function initialState(world: World): State;
export function playerObservation(world: World, state: State): Observation;
export function counterfactuals(world: World, state: State): CounterfactualPacket;
export function step(world: World, state: State, actionId: string): {
  reaction: string; next: State; writes: Write[]; squared_step_energy: number;
};
