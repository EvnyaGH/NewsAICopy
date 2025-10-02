import * as React from "react";
import { cn } from "@/lib/utils"; // 你们的 cn 函数

/**
 * Badge 组件
 * 用于显示文章分类、状态等小标签
 *
 * Props:
 * - variant: "default" | "secondary"，控制颜色
 * - className: 自定义 Tailwind class
 * - children: 标签文本
 */
function Badge({ variant = "secondary", className, children, ...props }) {
    return (
        <span
            data-slot="badge"
            className={cn(
                "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset",
                variant === "secondary"
                    ? "bg-secondary/20 text-secondary-foreground ring-secondary/50"
                    : "bg-primary/20 text-primary-foreground ring-primary/50",
                className
            )}
            {...props}
        >
      {children}
    </span>
    );
}

export { Badge };
