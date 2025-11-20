import dynamic from "next/dynamic";
import { GraphConfig } from "../types";

const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export function GraphComponent({
  graph,
  width,
  height,
}: {
  graph: GraphConfig;
  width: number;
  height: number;
}) {
  return (
    <ForceGraph
      height={height}
      width={width}
      graphData={{ nodes: graph.nodes, links: graph.links }}
      nodeLabel={(n) => n.id!}
      nodeColor={(n) =>
        n.data?.type === "entity"
          ? "orange"
          : n.data?.type === "idtype"
          ? "green"
          : n.data?.type === "upload"
          ? "red"
          : "gray"
      }
      nodeRelSize={2}
      linkLabel={(l) => `${JSON.stringify(l.data, null, 2)}`}
      linkColor={(l) =>
        l.data.type === "idtype-mapping"
          ? "green"
          : l.data.type === "1-1"
          ? "green"
          : l.data.type === "1-n"
          ? "orange"
          : l.data.type === "n-1"
          ? "orange"
          : l.data.type === "ordino-drilldown"
          ? "blue"
          : l.data.type === "ordino-drilldown-fragment"
          ? "rgba(0, 0, 255, 0.25)"
          : "gray"
      }
      linkLineDash={(l) =>
        ["ordino-drilldown-fragment", "n-1", "idtype-mapping"].includes(
          l.data.type
        )
          ? [3, 1]
          : undefined
      }
      linkDirectionalArrowLength={3.5}
      linkDirectionalArrowRelPos={1}
      linkCurvature={0.15}
      // dagMode="bu"
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.id as string;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Sans-Serif`;

        ctx.fillStyle =
          node.data?.type === "entity"
            ? "orange"
            : node.data?.type === "idtype"
            ? "green"
            : node.data?.type === "upload"
            ? "red"
            : "gray";

        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        if (
          node.data?.type !== "entity" &&
          node.data?.type !== "idtype" &&
          node.data?.type !== "upload"
        ) {
          ctx.fillText(label!, node.x!, node.y!);
          const textWidth = ctx.measureText(label!).width;
          ctx.beginPath();
          ctx.moveTo(node.x! - textWidth / 2, node.y!);
          ctx.lineTo(node.x! + textWidth / 2, node.y!);
          ctx.strokeStyle = "gray";
          ctx.lineWidth = 2 / globalScale;
          ctx.stroke();
        }
        ctx.fillText(label!, node.x!, node.y!);
      }}
      onNodeDragEnd={(node) => {
        node.fx = node.x;
        node.fy = node.y;
        node.fz = node.z;
      }}
      zoomToFit
    />
  );
}
