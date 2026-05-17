import { useQuery } from "@tanstack/react-query";
import { listCurricula, listSubjects, listTopics, listQuestionTypes } from "@/lib/api/taxonomy";

export function useCurricula() {
  return useQuery({
    queryKey: ["taxonomy", "curricula"],
    queryFn: () => listCurricula(),
    staleTime: 300_000, // 5 min, taxonomy rarely changes
  });
}

export function useSubjects(curriculumId?: string) {
  return useQuery({
    queryKey: ["taxonomy", "subjects", curriculumId],
    queryFn: () => listSubjects({ curriculum_id: curriculumId }),
    enabled: !!curriculumId,
    staleTime: 300_000,
  });
}

export function useTopics(subjectId?: string, parentId?: string) {
  return useQuery({
    queryKey: ["taxonomy", "topics", subjectId, parentId],
    queryFn: () => listTopics({ subject_id: subjectId, parent_id: parentId }),
    enabled: !!subjectId,
    staleTime: 300_000,
  });
}

export function useQuestionTypes() {
  return useQuery({
    queryKey: ["taxonomy", "question-types"],
    queryFn: () => listQuestionTypes(),
    staleTime: 600_000, // 10 min, essentially static
  });
}