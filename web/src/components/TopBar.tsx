"use client";

import { useAuth } from "@/context/AuthContext";
import { useLogout } from "@/hooks/useAuth";
import ThemeToggle from "./ThemeToggle";
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Menu,
  MenuItem,
  Box,
} from "@mui/material";
import { AccountCircle, Logout } from "@mui/icons-material";
import { useState } from "react";

export default function TopBar() {
  const { user } = useAuth();
  const logoutMutation = useLogout();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await logoutMutation.mutateAsync();
    handleClose();
  };

  return (
    <AppBar position="static" sx={{ ml: 240 }}>
      <Toolbar sx={{ justifyContent: "space-between" }}>
        <Typography variant="h6" component="div">
          管理中心
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <ThemeToggle />
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              keepMounted
              transformOrigin={{
                vertical: "top",
                horizontal: "right",
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              {user && <MenuItem onClick={handleClose}>{user.name}</MenuItem>}
              <MenuItem onClick={handleLogout}>
                <Logout sx={{ mr: 1 }} />
                退出登录
              </MenuItem>
            </Menu>
          </div>
        </Box>
      </Toolbar>
    </AppBar>
  );
}