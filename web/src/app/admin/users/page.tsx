"use client";

import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Box,
  Typography,
  TablePagination,
  TextField,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
} from "@mui/material";
import { Add, Delete, Refresh } from "@mui/icons-material";
import { useUsers, useDeleteUsers, useUserCount } from "@/hooks/useUsers";
import type { UserInfo } from "@/api/user";

export default function UsersPage() {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [keyword, setKeyword] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const usersQuery = useUsers({
    page: page + 1,
    size: pageSize,
    keyword: keyword || undefined,
  });

  const userCountQuery = useUserCount();
  const deleteMutation = useDeleteUsers();

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (searchTimeout) clearTimeout(searchTimeout);
    const timeout = setTimeout(() => {
      setKeyword(event.target.value);
      setPage(0);
    }, 300);
    setSearchTimeout(timeout);
  };

  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    const users = usersQuery.data?.data || [];
    if (event.target.checked) {
      setSelected(users.map((user: UserInfo) => user.id));
    } else {
      setSelected([]);
    }
  };

  const handleSelectOne = (event: React.ChangeEvent<HTMLInputElement>, id: string) => {
    if (event.target.checked) {
      setSelected((prev) => [...prev, id]);
    } else {
      setSelected((prev) => prev.filter((uid) => uid !== id));
    }
  };

  const handleDelete = () => {
    if (selected.length > 0) {
      deleteMutation.mutate(selected);
      setDeleteDialogOpen(false);
      setSelected([]);
    }
  };

  const isSelectedAll = usersQuery.data?.data?.length === selected.length && selected.length > 0;

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 3 }}>
        <Typography variant="h4">用户管理</Typography>
        <Box sx={{ display: "flex", gap: 2 }}>
          <Button
            variant="contained"
            color="error"
            startIcon={<Delete />}
            disabled={selected.length === 0 || deleteMutation.isPending}
            onClick={() => setDeleteDialogOpen(true)}
          >
            批量删除 ({selected.length})
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
          >
            新增用户
          </Button>
        </Box>
      </Box>

      <Box sx={{ display: "flex", gap: 2, mb: 3 }}>
        <TextField
          label="搜索用户名"
          placeholder="输入用户名搜索"
          variant="outlined"
          size="small"
          onChange={handleSearchChange}
          sx={{ width: 300 }}
        />
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={() => usersQuery.refetch()}
          disabled={usersQuery.isFetching}
        >
          刷新
        </Button>
      </Box>

      {usersQuery.error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          加载用户列表失败: {usersQuery.error.message}
        </Alert>
      )}

      {usersQuery.isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={isSelectedAll}
                      indeterminate={selected.length > 0 && !isSelectedAll}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>用户名</TableCell>
                  <TableCell>邮箱</TableCell>
                  <TableCell>角色</TableCell>
                  <TableCell>状态</TableCell>
                  <TableCell>创建时间</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {usersQuery.data?.data?.map((user: UserInfo) => (
                  <TableRow key={user.id}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selected.includes(user.id)}
                        onChange={(event) => handleSelectOne(event, user.id)}
                      />
                    </TableCell>
                    <TableCell>{user.username}</TableCell>
                    <TableCell>{user.email || "-"}</TableCell>
                    <TableCell>
                      <FormControl size="small" fullWidth>
                        <Select value={user.role} disabled>
                          <MenuItem value="admin">管理员</MenuItem>
                          <MenuItem value="user">普通用户</MenuItem>
                        </Select>
                      </FormControl>
                    </TableCell>
                    <TableCell>{user.is_active ? "启用" : "禁用"}</TableCell>
                    <TableCell>{new Date(user.created_at).toLocaleString()}</TableCell>
                    <TableCell>
                      <Box sx={{ display: "flex", gap: 1 }}>
                        <Button size="small">编辑</Button>
                        <Button size="small" color="error">删除</Button>
                        <Button size="small">重置密码</Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            component="div"
            count={userCountQuery.data?.data ?? 0}
            page={page}
            onPageChange={(_, newPage) => setPage(newPage)}
            rowsPerPage={pageSize}
            onRowsPerPageChange={(event) => {
              setPageSize(Number(event.target.value));
              setPage(0);
            }}
            rowsPerPageOptions={[10, 20, 50]}
          />
        </Paper>
      )}

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>确认删除</DialogTitle>
        <DialogContent>
          <Typography>确定要删除选中的 {selected.length} 个用户吗？</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>取消</Button>
          <Button color="error" onClick={handleDelete} disabled={deleteMutation.isPending}>
            确认删除
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}