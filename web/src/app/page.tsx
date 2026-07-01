"use client";

import {
  Box,
  Button,
  Container,
  Typography,
  Paper,
} from "@mui/material";
import {
  Login,
  AppRegistration,
  Memory,
  SmartToy,
  Cloud,
  Shield,
} from "@mui/icons-material";

const features = [
  {
    icon: <Memory />,
    title: "LLM 模型管理",
    description: "统一管理多种 LLM 模型，支持自定义配置参数",
  },
  {
    icon: <SmartToy />,
    title: "智能体编排",
    description: "创建和管理智能体，配置系统提示词和参数",
  },
  {
    icon: <Cloud />,
    title: "MCP 服务器",
    description: "连接和管理 MCP 服务器，扩展智能体能力",
  },
  {
    icon: <Shield />,
    title: "权限控制",
    description: "完善的用户角色管理，保障系统安全",
  },
];

export default function Home() {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          p: 8,
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ textAlign: "center", mb: 12 }}>
            <Typography variant="h3" sx={{ mb: 4, fontWeight: "bold" }}>
              欢迎使用 MCP Hub
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 8 }}>
              一站式 LLM 模型与智能体管理平台
            </Typography>
            <Box sx={{ display: "flex", gap: 3, justifyContent: "center" }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<Login />}
                href="/login"
              >
                登录
              </Button>
              <Button
                variant="outlined"
                size="large"
                startIcon={<AppRegistration />}
                href="/register"
              >
                注册
              </Button>
            </Box>
          </Box>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, 1fr)",
              },
              gap: 4,
            }}
          >
            {features.map((feature, index) => (
              <Paper
                key={index}
                sx={{
                  p: 4,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "flex-start",
                }}
              >
                <Box sx={{ color: "primary.main", mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {feature.description}
                </Typography>
              </Paper>
            ))}
          </Box>
        </Container>
      </Box>

      <Box sx={{ py: 4, textAlign: "center", borderTop: 1, borderColor: "divider" }}>
        <Typography variant="body2" color="text.secondary">
          MCP Hub Management Platform © 2026
        </Typography>
      </Box>
    </Box>
  );
}