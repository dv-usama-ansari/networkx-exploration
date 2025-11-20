export type GraphConfig = {
  directed: boolean;
  multigraph: boolean;
  graph: unknown;
  nodes: {
    id: string;
    data: unknown;
  }[];
  links: {
    source: string;
    target: string;
    data: unknown;
  }[];
};