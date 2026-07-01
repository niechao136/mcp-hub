"use client";

import { useUserCount } from "@/hooks/useUsers";
import { useLlmModelCount } from "@/hooks/useLlm";
import { useMcpServerCount } from "@/hooks/useMcp";
import { useAgentCount } from "@/hooks/useAgent";
import {
  Paper,
  Typography,
  Box,
  CircularProgress,
} from "@mui/material";
import { People, Memory, Chat, Settings } from "@mui/icons-material";

const StatCard = ({
  icon,
  label,
  value,
  loading,
}: {
  icon: React.ReactNode;
  label: string;
  value: number | undefined;
  loading: boolean;
}) => (
  <Paper sx={{ p: 4, display: "flex", flexDirection: "column" }}>
    <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
      <Box sx={{ mr: 2, color: "primary.main" }}>{icon}</Box>
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
    </Box>
    {loading ? (
      <CircularProgress size={24} />
    ) : (
      <Typography variant="h4">{value ?? 0}</Typography>
    )}
  </Paper>
);

export default function DashboardPage() {
  const userCountQuery = useUserCount();
  const llmCountQuery = useLlmModelCount();
  const mcpCountQuery = useMcpServerCount();
  const agentCountQuery = useAgentCount();

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 4 }}>
        仪表盘
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(2, 1fr)",
            md: "repeat(4, 1fr)",
          },
          gap: 3,
        }}
      >
        <StatCard
          icon={<People />}
          label="用户总数"
          value={userCountQuery.data?.data}
          loading={userCountQuery.isLoading}
        />
        <StatCard
          icon={<Memory />}
          label="LLM 模型"
          value={llmCountQuery.data?.data}
          loading={llmCountQuery.isLoading}
        />
        <StatCard
          icon={<Chat />}
          label="MCP 服务器"
          value={mcpCountQuery.data?.data}
          loading={mcpCountQuery.isLoading}
        />
        <StatCard
          icon={<Settings />}
          label="智能体"
          value={agentCountQuery.data?.data}
          loading={agentCountQuery.isLoading}
        />
      </Box>
    </Box>
  );
}