"use client"

import type React from "react"
import { useState } from "react"
import { TextField, InputAdornment, IconButton, FormHelperText, Box, Typography } from "@mui/material"
import { Visibility, VisibilityOff, Error as ErrorIcon } from "@mui/icons-material"

export interface InputProps {
  variant?: "text" | "textarea" | "password"
  label: string
  placeholder?: string
  value: string
  onChange: (value: string) => void
  error?: string
  helpText?: string
  disabled?: boolean
  required?: boolean
  rows?: number
  type?: string
}

export const Input: React.FC<InputProps> = ({
  variant = "text",
  label,
  placeholder,
  value,
  onChange,
  error,
  helpText,
  disabled = false,
  required = false,
  rows = 4,
  type,
}) => {
  const [showPassword, setShowPassword] = useState(false)

  const isPassword = variant === "password"
  const isTextarea = variant === "textarea"

  const inputType = isPassword ? (showPassword ? "text" : "password") : type || "text"

  return (
    <Box sx={{ width: "100%" }}>
      <Typography
        component="label"
        sx={{
          display: "block",
          fontSize: "14px",
          fontWeight: 500,
          color: "#2C3E50",
          marginBottom: "8px",
        }}
      >
        {label}
        {required && (
          <Typography component="span" sx={{ color: "#EF4444", marginLeft: "4px" }}>
            *
          </Typography>
        )}
      </Typography>

      <TextField
        fullWidth
        multiline={isTextarea}
        rows={isTextarea ? rows : undefined}
        type={inputType}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        error={!!error}
        required={required}
        slotProps={{
          input: {
            endAdornment: isPassword ? (
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                  size="small"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ) : undefined,
          },
        }}
        sx={{
          "& .MuiOutlinedInput-root": {
            minHeight: isTextarea ? "auto" : "44px",
            fontSize: "14px",
            fontWeight: 400,
            borderRadius: "8px",
            "& input::placeholder, & textarea::placeholder": {
              color: "#7F8C8D",
              opacity: 1,
            },
            "& fieldset": {
              borderColor: "#E0E4E8",
              borderWidth: "1px",
            },
            "&:hover fieldset": {
              borderColor: "#A16AE8",
            },
            "&.Mui-focused fieldset": {
              borderWidth: "2px",
              borderColor: "#A16AE8",
            },
            "&.Mui-error fieldset": {
              borderWidth: "2px",
              borderColor: "#EF4444",
            },
          },
        }}
      />

      {error && (
        <FormHelperText
          error
          sx={{
            display: "flex",
            alignItems: "center",
            gap: "4px",
            fontSize: "12px",
            color: "#EF4444",
            marginTop: "4px",
            marginLeft: 0,
          }}
        >
          <ErrorIcon sx={{ fontSize: "14px" }} />
          {error}
        </FormHelperText>
      )}

      {helpText && !error && (
        <FormHelperText
          sx={{
            fontSize: "12px",
            color: "#7F8C8D",
            marginTop: "4px",
            marginLeft: 0,
          }}
        >
          {helpText}
        </FormHelperText>
      )}
    </Box>
  )
}
