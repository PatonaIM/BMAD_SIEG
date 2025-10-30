"use client"

import { Box, Typography, LinearProgress } from "@mui/material"
import { motion } from "framer-motion"
import { styled } from "@mui/material/styles"

export interface InterviewProgressProps {
  current: number
  total: number
}

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  backgroundColor: theme.palette.grey[200],
  "& .MuiLinearProgress-bar": {
    borderRadius: 4,
    backgroundColor: theme.palette.primary.main,
  },
}))

/**
 * InterviewProgress Component
 * Displays progress bar and text showing question completion
 */
export default function InterviewProgress({ current, total }: InterviewProgressProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0

  return (
    <Box
      sx={{
        position: "sticky",
        top: 0,
        bgcolor: "background.paper",
        p: 2,
        borderBottom: "1px solid",
        borderColor: "grey.300",
        zIndex: 10,
      }}
    >
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontWeight: 500 }}>
          Question {current} of {total} ({percentage}% complete)
        </Typography>

        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{ transformOrigin: "left" }}
        >
          <StyledLinearProgress variant="determinate" value={percentage} />
        </motion.div>
      </motion.div>
    </Box>
  )
}
