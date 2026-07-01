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
import { useMcpServers, useMcpServerCount, useDeleteMcpServers, useCreateMcpServer, useUpdateMcpServer } from "@/hooks/useMcp";
import { McpServer, McpCreate, McpUpdate } from "@/api/mcp";

export default function McpPage() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [keyword, setKeyword] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingServer, setEditingServer] = useState<McpServer | null>(null);
  const [createForm, setCreateForm] = useState<McpCreate>({
    name: "",
    transport: "sse",
  });
  const [editForm, setEditForm] = useState<McpUpdate>({});

  const mcpQuery = useMcpServers({
    page: page + 1,
    size: pageSize,
    keyword: keyword || undefined,
  });

  const mcpCountQuery = useMcpServerCount();
  const deleteMutation = useDeleteMcpServers();
  const createMutation = useCreateMcpServer();
  const updateMutation = useUpdateMcpServer();

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    const servers = mcpQuery.data?.data || [];
    if (event.target.checked) {
      setSelected(servers.map((server: McpServer) => server.id));
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
    setCreateForm({ name: "", transport: "sse" });
    setOpenCreateDialog(true);
  };

  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
  };

  const handleSubmitCreate = () => {
    createMutation.mutate(createForm);
    setOpenCreateDialog(false);
  };

  const handleOpenEditDialog = (server: McpServer) => {
    setEditingServer(server);
    setEditForm({
      name: server.name,
      description: server.description || undefined,
      transport: server.transport,
      url: server.url || undefined,
    });
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    setEditingServer(null);
  };

  const handleSubmitEdit = () => {
    if (editingServer) {
      updateMutation.mutate({ serverId: editingServer.id, data: editForm });
    }
    setOpenEditDialog(false);
  };

  const isSelectedAll = mcpQuery.data?.data?.length === selected.length && selected.length > 0;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">MCP 服务器管理</Typography>
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
            添加服务器
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Search />
          <TextField
            placeholder="搜索服务器名称"
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
              <TableCell>服务器名称</TableCell>
              <TableCell>传输方式</TableCell>
              <TableCell>URL</TableCell>
              <TableCell>状态</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {mcpQuery.data?.data?.map((server: McpServer) => (
              <TableRow key={server.id}>
                <TableCell padding="checkbox">
                  <Checkbox checked={selected.includes(server.id)} onChange={() => handleSelect(server.id)} />
                </TableCell>
                <TableCell>{server.name}</TableCell>
                <TableCell>{server.transport}</TableCell>
                <TableCell>{server.url || "-"}</TableCell>
                <TableCell>{server.status}</TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title="编辑">
                      <IconButton onClick={() => handleOpenEditDialog(server)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="删除">
                      <IconButton onClick={() => handleDelete(server.id)}>
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
        count={mcpCountQuery.data?.data || 0}
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
        <DialogTitle>添加 MCP 服务器</DialogTitle>
        <DialogContent>
          <TextField
            label="服务器名称"
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
            label="传输方式"
            fullWidth
            margin="normal"
            value={createForm.transport}
            onChange={(e) => setCreateForm({ ...createForm, transport: e.target.value })}
          />
          <TextField
            label="URL"
            fullWidth
            margin="normal"
            value={createForm.url || ""}
            onChange={(e) => setCreateForm({ ...createForm, url: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog}>取消</Button>
          <Button onClick={handleSubmitCreate}>确定</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openEditDialog} onClose={handleCloseEditDialog}>
        <DialogTitle>编辑 MCP 服务器</DialogTitle>
        <DialogContent>
          <TextField
            label="服务器名称"
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
            label="传输方式"
            fullWidth
            margin="normal"
            value={editForm.transport || ""}
            onChange={(e) => setEditForm({ ...editForm, transport: e.target.value })}
          />
          <TextField
            label="URL"
            fullWidth
            margin="normal"
            value={editForm.url || ""}
            onChange={(e) => setEditForm({ ...editForm, url: e.target.value })}
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