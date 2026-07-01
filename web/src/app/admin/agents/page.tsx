"use client";

import { useState } from "react";
import {
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Typography,
  IconButton,
  Tooltip,
} from "@mui/material";
import { Delete, Edit, Add, Search } from "@mui/icons-material";
import { useAgents, useAgentCount, useDeleteAgents, useCreateAgent, useUpdateAgent } from "@/hooks/useAgent";
import { Agent, AgentCreate, AgentUpdate } from "@/api/agent";

export default function AgentsPage() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [keyword, setKeyword] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [createForm, setCreateForm] = useState<AgentCreate>({
    name: "",
    llm_model_id: "",
    system_prompt: "",
  });
  const [editForm, setEditForm] = useState<AgentUpdate>({});

  const agentQuery = useAgents({
    page: page + 1,
    size: pageSize,
    keyword: keyword || undefined,
  });

  const agentCountQuery = useAgentCount();
  const deleteMutation = useDeleteAgents();
  const createMutation = useCreateAgent();
  const updateMutation = useUpdateAgent();

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    const agents = agentQuery.data?.data || [];
    if (event.target.checked) {
      setSelected(agents.map((agent: Agent) => agent.id));
    } else {
      setSelected([]);
    }
  };

  const handleSelect = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleDelete = (id: string) => {
    deleteMutation.mutate([id]);
  };

  const handleBatchDelete = () => {
    if (selected.length > 0) {
      deleteMutation.mutate(selected);
      setSelected([]);
    }
  };

  const handleOpenCreateDialog = () => {
    setCreateForm({ name: "", llm_model_id: "", system_prompt: "" });
    setOpenCreateDialog(true);
  };

  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
  };

  const handleSubmitCreate = () => {
    createMutation.mutate(createForm);
    setOpenCreateDialog(false);
  };

  const handleOpenEditDialog = (agent: Agent) => {
    setEditingAgent(agent);
    setEditForm({
      name: agent.name,
      description: agent.description || undefined,
      llm_model_id: agent.llm_model_id,
      system_prompt: agent.system_prompt,
      temperature: agent.temperature,
      max_tokens: agent.max_tokens || undefined,
      memory_strategy: agent.memory_strategy,
      memory_window: agent.memory_window,
      is_active: agent.is_active,
    });
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    setEditingAgent(null);
  };

  const handleSubmitEdit = () => {
    if (editingAgent) {
      updateMutation.mutate({ agentId: editingAgent.id, data: editForm });
    }
    setOpenEditDialog(false);
  };

  const isSelectedAll = agentQuery.data?.data?.length === selected.length && selected.length > 0;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">智能体管理</Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Delete />}
            disabled={selected.length === 0}
            onClick={handleBatchDelete}
          >
            批量删除 ({selected.length})
          </Button>
          <Button variant="contained" startIcon={<Add />} onClick={handleOpenCreateDialog}>
            添加智能体
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Search />
          <TextField
            placeholder="搜索智能体名称"
            value={keyword}
            onChange={(e) => {
              setKeyword(e.target.value);
              setPage(0);
            }}
            fullWidth
          />
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selected.length > 0 && !isSelectedAll}
                  checked={isSelectedAll}
                  onChange={handleSelectAll}
                />
              </TableCell>
              <TableCell>智能体名称</TableCell>
              <TableCell>LLM 模型</TableCell>
              <TableCell>温度</TableCell>
              <TableCell>记忆策略</TableCell>
              <TableCell>是否启用</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {agentQuery.data?.data?.map((agent: Agent) => (
              <TableRow key={agent.id}>
                <TableCell padding="checkbox">
                  <Checkbox checked={selected.includes(agent.id)} onChange={() => handleSelect(agent.id)} />
                </TableCell>
                <TableCell>{agent.name}</TableCell>
                <TableCell>{agent.llm_model_name || "-"}</TableCell>
                <TableCell>{agent.temperature}</TableCell>
                <TableCell>{agent.memory_strategy}</TableCell>
                <TableCell>{agent.is_active ? "是" : "否"}</TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title="编辑">
                      <IconButton onClick={() => handleOpenEditDialog(agent)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="删除">
                      <IconButton onClick={() => handleDelete(agent.id)}>
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={agentCountQuery.data?.data || 0}
        page={page}
        onPageChange={(_, newPage) => setPage(newPage)}
        rowsPerPage={pageSize}
        onRowsPerPageChange={(e) => {
          setPageSize(Number(e.target.value));
          setPage(0);
        }}
        rowsPerPageOptions={[5, 10, 25]}
      />

      <Dialog open={openCreateDialog} onClose={handleCloseCreateDialog}>
        <DialogTitle>添加智能体</DialogTitle>
        <DialogContent>
          <TextField
            label="智能体名称"
            fullWidth
            margin="normal"
            value={createForm.name}
            onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
          />
          <TextField
            label="描述"
            fullWidth
            margin="normal"
            value={createForm.description || ""}
            onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
          />
          <TextField
            label="LLM 模型 ID"
            fullWidth
            margin="normal"
            value={createForm.llm_model_id}
            onChange={(e) => setCreateForm({ ...createForm, llm_model_id: e.target.value })}
          />
          <TextField
            label="系统提示词"
            fullWidth
            margin="normal"
            multiline
            rows={4}
            value={createForm.system_prompt}
            onChange={(e) => setCreateForm({ ...createForm, system_prompt: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog}>取消</Button>
          <Button onClick={handleSubmitCreate}>确定</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openEditDialog} onClose={handleCloseEditDialog}>
        <DialogTitle>编辑智能体</DialogTitle>
        <DialogContent>
          <TextField
            label="智能体名称"
            fullWidth
            margin="normal"
            value={editForm.name || ""}
            onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
          />
          <TextField
            label="描述"
            fullWidth
            margin="normal"
            value={editForm.description || ""}
            onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
          />
          <TextField
            label="LLM 模型 ID"
            fullWidth
            margin="normal"
            value={editForm.llm_model_id || ""}
            onChange={(e) => setEditForm({ ...editForm, llm_model_id: e.target.value })}
          />
          <TextField
            label="系统提示词"
            fullWidth
            margin="normal"
            multiline
            rows={4}
            value={editForm.system_prompt || ""}
            onChange={(e) => setEditForm({ ...editForm, system_prompt: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog}>取消</Button>
          <Button onClick={handleSubmitEdit}>确定</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}