"use client";

import dynamic from "next/dynamic";
import * as React from "react";
import { GraphConfig } from "../../types";

const ForceGraph = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

export function Graph2D({
  graph,
  width,
  height,
}: {
  graph: GraphConfig;
  width: number;
  height: number;
}) {
  // Count links in each direction separately
  const directedLinkCount = React.useMemo(
    () =>
      graph.links.reduce((acc, l) => {
        const key = `${l.source}-${l.target}`;
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
    [graph.links]
  );

  // Create curvature arrays for each direction
  const linkCurvatureMap = React.useMemo(
    () =>
      Object.keys(directedLinkCount).reduce((acc, key) => {
        const count = directedLinkCount[key];
        acc[key] =
          count > 1
            ? Array.from({ length: count }, (_, i) => 0.15 * (i + 1))
            : [0.15];
        return acc;
      }, {} as Record<string, number[]>),
    [directedLinkCount]
  );

  // Assign each link a specific curvature index based on direction
  const linkToCurvatureIndex = React.useMemo(() => {
    const indexMap: Record<string, number> = {};
    const counters: Record<string, number> = {};

    graph.links.forEach((l) => {
      const directionKey = `${l.source}-${l.target}`;
      const linkId = `${l.source}-${l.target}-${
        (l.data as { type: string })?.type || ""
      }-${
        (
          l.data as { workbench: { views: { name: string }[] } }
        )?.workbench?.views
          ?.map((v) => v.name)
          .join(",") || ""
      }`;

      if (!counters[directionKey]) {
        counters[directionKey] = 0;
      }

      indexMap[linkId] = counters[directionKey]++;
    });

    return indexMap;
  }, [graph.links]);

  return (
    <ForceGraph
      height={height}
      width={width}
      graphData={{ nodes: graph.nodes, links: graph.links }}
      nodeColor={(n) =>
        n.data?.type === "entity"
          ? "orange"
          : n.data?.type === "idtype"
          ? "green"
          : n.data?.type === "upload"
          ? "red"
          : "gray"
      }
      // nodeId={(n) => n.id as string}
      nodeRelSize={8}
      linkLabel={(l) => `${JSON.stringify(l.data, null, 2)}`}
      linkColor={(l) =>
        l.data.type === "idtype-mapping"
          ? "green"
          : l.data.type === "1-1"
          ? l.data.via_idtype
            ? "lightgreen"
            : "green"
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
        l.data.is_derived
          ? [3, 1]
          : null
      }
      linkDirectionalArrowLength={3.5}
      linkDirectionalArrowRelPos={1}
      linkCurvature={(l) => {
        const directionKey = `${(l.source as { id: string })?.id}-${
          (l.target as { id: string })?.id
        }`;
        const linkId = `${(l.source as { id: string })?.id}-${
          (l.target as { id: string })?.id
        }-${(l.data as { type: string })?.type || ""}-${
          (
            l.data as { workbench: { views: { name: string }[] } }
          )?.workbench?.views
            ?.map((v) => v.name)
            .join(",") || ""
        }`;

        if (linkCurvatureMap[directionKey]?.length > 1) {
          const index = linkToCurvatureIndex[linkId] || 0;
          const curvature =
            linkCurvatureMap[directionKey][
              index % linkCurvatureMap[directionKey].length
            ];
          return curvature;
        }
        return 0.15;
      }}
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
    />
  );
}
