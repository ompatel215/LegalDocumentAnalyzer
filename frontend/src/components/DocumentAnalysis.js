import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemText,
  Alert,
  LinearProgress,
  Divider
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DescriptionIcon from '@mui/icons-material/Description';
import AssessmentIcon from '@mui/icons-material/Assessment';
import WarningIcon from '@mui/icons-material/Warning';
import SummarizeIcon from '@mui/icons-material/Summarize';

const DocumentAnalysis = () => {
  const { documentId } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await axios.get(`/api/v1/documents/${documentId}/analysis`);
        setAnalysis(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load document analysis');
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [documentId]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  const getRiskColor = (score) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Document Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item>
            <DescriptionIcon fontSize="large" />
          </Grid>
          <Grid item xs>
            <Typography variant="h4">{analysis.filename}</Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Uploaded on {new Date(analysis.upload_date).toLocaleDateString()}
            </Typography>
          </Grid>
          <Grid item>
            <Chip
              label={analysis.classification.document_type}
              color="primary"
              variant="outlined"
            />
          </Grid>
        </Grid>
      </Paper>

      <Grid container spacing={4}>
        {/* Summary Section */}
        <Grid item xs={12}>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <SummarizeIcon sx={{ mr: 2 }} />
                <Typography variant="h6">Executive Summary</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Typography paragraph>{analysis.summary.executive_summary}</Typography>
              <Typography variant="h6" sx={{ mt: 2 }}>Key Points</Typography>
              <List>
                {analysis.summary.key_points.map((point, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={point.text}
                      secondary={`Category: ${point.category}`}
                    />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Risk Analysis Section */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <WarningIcon sx={{ mr: 2 }} />
                <Typography variant="h6">Risk Analysis</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box mb={3}>
                <Typography variant="h6" gutterBottom>Overall Risk Score</Typography>
                <LinearProgress
                  variant="determinate"
                  value={analysis.risk_analysis.overall_risk_score * 100}
                  color={getRiskColor(analysis.risk_analysis.overall_risk_score)}
                  sx={{ height: 10, borderRadius: 5 }}
                />
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {(analysis.risk_analysis.overall_risk_score * 100).toFixed(1)}%
                </Typography>
              </Box>

              <Typography variant="h6" gutterBottom>Risk Summary</Typography>
              <List>
                {analysis.risk_analysis.risk_summary.map((item, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={item} />
                  </ListItem>
                ))}
              </List>

              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>Recommendations</Typography>
              <List>
                {analysis.risk_analysis.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </AccordionDetails>
          </Accordion>
        </Grid>

        {/* Detailed Analysis Section */}
        <Grid item xs={12}>
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center">
                <AssessmentIcon sx={{ mr: 2 }} />
                <Typography variant="h6">Detailed Analysis</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={3}>
                {/* Legal Entities */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Legal Entities</Typography>
                  {Object.entries(analysis.analysis.legal_entities).map(([type, entities]) => (
                    <Box key={type} mb={2}>
                      <Typography variant="subtitle1">{type}</Typography>
                      <Box display="flex" flexWrap="wrap" gap={1}>
                        {entities.map((entity, index) => (
                          <Chip key={index} label={entity} size="small" />
                        ))}
                      </Box>
                    </Box>
                  ))}
                </Grid>

                {/* Key Terms */}
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Key Terms</Typography>
                  <List dense>
                    {analysis.analysis.key_terms.map((term, index) => (
                      <ListItem key={index}>
                        <ListItemText
                          primary={term.term}
                          secondary={`Frequency: ${term.frequency}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Grid>

                {/* Section Summaries */}
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>Section Summaries</Typography>
                  {analysis.summary.section_summaries.map((section, index) => (
                    <Box key={index} mb={3}>
                      <Typography variant="subtitle1" gutterBottom>
                        {section.title}
                      </Typography>
                      <Typography paragraph>{section.summary}</Typography>
                      <Box display="flex" flexWrap="wrap" gap={1}>
                        {section.key_terms.map((term, termIndex) => (
                          <Chip
                            key={termIndex}
                            label={`${term.term} (${term.frequency})`}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                      <Divider sx={{ mt: 2 }} />
                    </Box>
                  ))}
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </Grid>
      </Grid>
    </Container>
  );
};

export default DocumentAnalysis; 