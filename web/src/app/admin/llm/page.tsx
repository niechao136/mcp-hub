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
import { useLlmModels, useLlmModelCount, useDeleteLlmModels, useCreateLlmModel, useUpdateLlmModel } from "@/hooks/useLlm";
import { LlmModel, LlmCreate, LlmUpdate } from "@/api/llm";

export default function LlmPage() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [keyword, setKeyword] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openEditDialog, setOpenEditDialog] = useState(false);
  const [editingModel, setEditingModel] = useState<LlmModel | null>(null);
  const [createForm, setCreateForm] = useState<LlmCreate>({
    display_name: "",
    provider: "",
    model_id: "",
  });
  const [editForm, setEditForm] = useState<LlmUpdate>({});

  const llmQuery = useLlmModels({
    page: page + 1,
    size: pageSize,
    keyword: keyword || undefined,
  });

  const llmCountQuery = useLlmModelCount();
  const deleteMutation = useDeleteLlmModels();
  const createMutation = useCreateLlmModel();
  const updateMutation = useUpdateLlmModel();

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    const models = llmQuery.data?.data || [];
    if (event.target.checked) {
      setSelected(models.map((model: LlmModel) => model.id));
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
    setCreateForm({ display_name: "", provider: "", model_id: "" });
    setOpenCreateDialog(true);
  };

  const handleCloseCreateDialog = () => {
    setOpenCreateDialog(false);
  };

  const handleSubmitCreate = () => {
    createMutation.mutate(createForm);
    setOpenCreateDialog(false);
  };

  const handleOpenEditDialog = (model: LlmModel) => {
    setEditingModel(model);
    setEditForm({
      display_name: model.display_name,
      provider: model.provider,
      model_id: model.model_id,
      base_url: model.base_url || undefined,
      context_window: model.context_window || undefined,
      max_tokens: model.max_tokens || undefined,
      supports_tool_call: model.supports_tool_call,
      supports_vision: model.supports_vision,
      is_active: model.is_active,
    });
    setOpenEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setOpenEditDialog(false);
    setEditingModel(null);
  };

  const handleSubmitEdit = () => {
    if (editingModel) {
      updateMutation.mutate({ modelId: editingModel.id, data: editForm });
    }
    setOpenEditDialog(false);
  };

  const isSelectedAll = llmQuery.data?.data?.length === selected.length && selected.length > 0;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">LLM 模型管理</Typography>
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
            添加模型
          </Button>
        </Box>
      </Box>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
          <Search />
          <TextField
            placeholder="搜索模型名称"
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
              <TableCell>模型名称</TableCell>
              <TableCell>提供商</TableCell>
              <TableCell>模型 ID</TableCell>
              <TableCell>上下文窗口</TableCell>
              <TableCell>是否启用</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {llmQuery.data?.data?.map((model: LlmModel) => (
              <TableRow key={model.id}>
                <TableCell padding="checkbox">
                  <Checkbox checked={selected.includes(model.id)} onChange={() => handleSelect(model.id)} />
                </TableCell>
                <TableCell>{model.display_name}</TableCell>
                <TableCell>{model.provider}</TableCell>
                <TableCell>{model.model_id}</TableCell>
                <TableCell>{model.context_window || "-"}</TableCell>
                <TableCell>{model.is_active ? "是" : "否"}</TableCell>
                <TableCell>
                  <Box sx={{ display: "flex", gap: 1 }}>
                    <Tooltip title="编辑">
                      <IconButton onClick={() => handleOpenEditDialog(model)}>
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="删除">
                      <IconButton onClick={() => handleDelete(model.id)}>
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
        count={llmCountQuery.data?.data || 0}
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
        <DialogTitle>添加 LLM 模型</DialogTitle>
        <DialogContent>
          <TextField
            label="显示名称"
            fullWidth
            margin="normal"
            value={createForm.display_name}
            onChange={(e) => setCreateForm({ ...createForm, display_name: e.target.value })}
          />
          <TextField
            label="提供商"
            fullWidth
            margin="normal"
            value={createForm.provider}
            onChange={(e) => setCreateForm({ ...createForm, provider: e.target.value })}
          />
          <TextField
            label="模型 ID"
            fullWidth
            margin="normal"
            value={createForm.model_id}
            onChange={(e) => setCreateForm({ ...createForm, model_id: e.target.value })}
          />
          <TextField
            label="基础 URL"
            fullWidth
            margin="normal"
            value={createForm.base_url || ""}
            onChange={(e) => setCreateForm({ ...createForm, base_url: e.target.value })}
          />
          <TextField
            label="API Key"
            type="password"
            fullWidth
            margin="normal"
            value={createForm.api_key || ""}
            onChange={(e) => setCreateForm({ ...createForm, api_key: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCreateDialog}>取消</Button>
          <Button onClick={handleSubmitCreate}>确定</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openEditDialog} onClose={handleCloseEditDialog}>
        <DialogTitle>编辑 LLM 模型</DialogTitle>
        <DialogContent>
          <TextField
            label="显示名称"
            fullWidth
            margin="normal"
            value={editForm.display_name || ""}
            onChange={(e) => setEditForm({ ...editForm, display_name: e.target.value })}
          />
          <TextField
            label="提供商"
            fullWidth
            margin="normal"
            value={editForm.provider || ""}
            onChange={(e) => setEditForm({ ...editForm, provider: e.target.value })}
          />
          <TextField
            label="模型 ID"
            fullWidth
            margin="normal"
            value={editForm.model_id || ""}
            onChange={(e) => setEditForm({ ...editForm, model_id: e.target.value })}
          />
          <TextField
            label="基础 URL"
            fullWidth
            margin="normal"
            value={editForm.base_url || ""}
            onChange={(e) => setEditForm({ ...editForm, base_url: e.target.value })}
          />
          <TextField
            label="API Key"
            type="password"
            fullWidth
            margin="normal"
            value={editForm.api_key || ""}
            onChange={(e) => setEditForm({ ...editForm, api_key: e.target.value })}
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