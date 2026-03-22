"use client";

import { useT } from "@/lib/i18n";
import type { Item } from "@/lib/types";

interface Props {
  items: Item[];
  gold: number;
}

export function InventoryPanel({ items, gold }: Props) {
  const t = useT();

  return (
    <div className="p-4 fantasy-card m-3">
      <h3 className="section-title mb-3">{t("sidebar.inventory")}</h3>

      {/* Gold display */}
      <div
        className="flex items-center gap-2 mb-3 px-3 py-2 rounded"
        style={{ background: "rgba(194,58,46,0.04)", border: "1px solid rgba(194,58,46,0.1)" }}
      >
        <span className="text-gold text-sm">&#9733;</span>
        <span className="text-gold font-medieval font-bold text-sm">{gold}</span>
        <span style={{ color: "rgba(194,58,46,0.4)", fontSize: "13px" }}>{t("sidebar.goldCoins")}</span>
      </div>

      {/* Items */}
      {items.length === 0 ? (
        <div className="text-center py-4">
          <p style={{ color: "rgba(255,255,255,0.2)", fontSize: "13px" }} className="font-body">
            {t("sidebar.emptyPockets")}
          </p>
        </div>
      ) : (
        <div className="space-y-1">
          {items.map((item) => (
            <div
              key={item.id}
              className="tooltip-trigger group flex items-center gap-2 px-3 py-2 rounded
                         transition-all duration-200 cursor-default"
              style={{ fontSize: "14px" }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.03)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = "transparent";
              }}
            >
              <div className="flex-1 min-w-0">
                <span style={{ color: "rgba(255,255,255,0.6)" }} className="font-body block truncate">
                  {item.name}
                </span>
              </div>
              <span style={{ color: "rgba(194,58,46,0.3)", fontSize: "12px" }} className="font-mono">
                {item.value}g
              </span>
              {item.description && (
                <div className="tooltip-content">{item.description}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
