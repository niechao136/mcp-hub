"use client";

import { usePathname } from "next/navigation";
import {
  Dashboard,
  People,
  Memory,
  Chat,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "@mui/icons-material";
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Toolbar,
  Typography,
} from "@mui/material";
import { useState } from "react";

interface MenuItem {
  icon: React.ReactNode;
  label: string;
  path: string;
}

const menuItems: MenuItem[] = [
  { icon: <Dashboard />, label: "仪表盘", path: "/admin" },
  { icon: <People />, label: "用户管理", path: "/admin/users" },
  { icon: <Memory />, label: "LLM 模型", path: "/admin/llm" },
  { icon: <Chat />, label: "MCP 服务器", path: "/admin/mcp" },
  { icon: <Settings />, label: "智能体", path: "/admin/agents" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(true);

  return (
    <Drawer
      variant="permanent"
      open={open}
      sx={{
        width: open ? 240 : 64,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: open ? 240 : 64,
          boxSizing: "border-box",
        },
      }}
    >
      <Toolbar sx={{ justifyContent: "space-between", px: 2 }}>
        {open && (
          <Typography variant="h6" component="div">
            MCP Hub
          </Typography>
        )}
        <IconButton onClick={() => setOpen(!open)}>
          {open ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              sx={{
                minHeight: 48,
                justifyContent: open ? "initial" : "center",
                px: 2.5,
              }}
              href={item.path}
              selected={pathname === item.path}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: open ? 3 : "auto",
                  justifyContent: "center",
                }}
              >
                {item.icon}
              </ListItemIcon>
              {open && <ListItemText primary={item.label} />}
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}