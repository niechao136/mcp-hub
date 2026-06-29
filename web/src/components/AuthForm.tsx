"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Button,
  Container,
  CssBaseline,
  TextField,
  Typography,
  Link,
  Alert,
} from "@mui/material";
import { useForm } from "react-hook-form";
import { useLogin, useRegister } from "@/hooks/useAuth";
import { UserLogin, UserRegister } from "@/api/auth";

interface AuthFormProps {
  mode: "login" | "register";
}

export default function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string>("");
  
  const loginMutation = useLogin();
  const registerMutation = useRegister();

  const { register, handleSubmit, formState: { errors } } = useForm<
    mode extends "login" ? UserLogin : UserRegister
  >({
    defaultValues: {
      username: "",
      password: "",
      ...(mode === "register" && { email: "" }),
    },
  });

  const onSubmit = async (data: UserLogin | UserRegister) => {
    setError("");

    if (mode === "login") {
      const result = await loginMutation.mutateAsync(data as UserLogin);
      if (result.status !== 1) {
        setError(result.msg);
        return;
      }
      router.push("/");
    } else {
      const result = await registerMutation.mutateAsync(data as UserRegister);
      if (result.status !== 1) {
        setError(result.msg);
        return;
      }
      router.push("/login");
    }
  };

  const isLoading = mode === "login" ? loginMutation.isPending : registerMutation.isPending;

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <Box
        sx={{
          marginTop: 8,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <Typography component="h1" variant="h5">
          {mode === "login" ? "登录" : "注册"}
        </Typography>
        <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 1, width: "100%" }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            label="用户名"
            autoFocus
            {...register("username", { required: "用户名不能为空" })}
            error={!!errors.username}
            helperText={errors.username?.message}
          />
          
          {mode === "register" && (
            <TextField
              margin="normal"
              fullWidth
              label="邮箱"
              type="email"
              {...register("email")}
              error={!!errors.email}
              helperText={errors.email?.message}
            />
          )}
          
          <TextField
            margin="normal"
            required
            fullWidth
            label="密码"
            type="password"
            {...register("password", { required: "密码不能为空" })}
            error={!!errors.password}
            helperText={errors.password?.message}
          />
          
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={isLoading}
          >
            {isLoading ? "加载中..." : (mode === "login" ? "登录" : "注册")}
          </Button>
          
          <Typography variant="body2" align="center">
            {mode === "login" ? "还没有账号？" : "已有账号？"}
            <Link href={mode === "login" ? "/register" : "/login"} variant="body2">
              {mode === "login" ? "立即注册" : "立即登录"}
            </Link>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
}