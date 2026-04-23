export type SentimentSummary = {
  total_documents: number;
  positive: number;
  neutral: number;
  negative: number;
};

export type TargetSentiment = {
  target_name: string;
  mentions: number;
  positive_mentions: number;
  neutral_mentions: number;
  negative_mentions: number;
};

export type AssessmentSentiment = {
  assessment_text: string;
  mentions: number;
  positive_mentions: number;
  neutral_mentions: number;
  negative_mentions: number;
};

export type FeedItem = {
  id: number;
  source: string;
  topic_label: string | null;
  content: string;
  published_at: string | null;
  overall_sentiment: string | null;
};

type FeedResponse = {
  items: FeedItem[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return fallback;
    }

    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getSentimentSummary(): Promise<SentimentSummary> {
  return fetchJson<SentimentSummary>("/sentiment/summary", {
    total_documents: 0,
    positive: 0,
    neutral: 0,
    negative: 0,
  });
}

export async function getTargets(): Promise<TargetSentiment[]> {
  return fetchJson<TargetSentiment[]>("/sentiment/targets", []);
}

export async function getAssessments(): Promise<AssessmentSentiment[]> {
  return fetchJson<AssessmentSentiment[]>("/sentiment/assessments", []);
}

export async function getFeed(): Promise<FeedItem[]> {
  const response = await fetchJson<FeedResponse>("/feed", { items: [] });
  return response.items;
}
