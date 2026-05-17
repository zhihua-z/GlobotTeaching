"use client";

import { useState } from "react";
import { ChevronRight, ChevronDown } from "lucide-react";

interface TopicNode {
  id: string;
  name: string;
  slug: string;
  depth: number;
  children?: TopicNode[];
}

interface TaxonomyTreeProps {
  curricula: { id: string; code: string; name: string }[];
  subjects: { id: string; code: string; name: string }[];
  topics: TopicNode[];
  onSelectCurriculum?: (id: string) => void;
  onSelectSubject?: (id: string) => void;
  onSelectTopic?: (id: string) => void;
}

function TopicBranch({
  topic,
  onSelect,
  depth = 0,
}: {
  topic: TopicNode;
  onSelect?: (id: string) => void;
  depth?: number;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasChildren = topic.children && topic.children.length > 0;

  return (
    <div>
      <button
        type="button"
        className="flex items-center gap-1 w-full text-left px-2 py-1 text-sm hover:bg-accent rounded-sm"
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
        onClick={() => {
          onSelect?.(topic.id);
          if (hasChildren) setExpanded(!expanded);
        }}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown className="h-3 w-3 shrink-0" />
          ) : (
            <ChevronRight className="h-3 w-3 shrink-0" />
          )
        ) : (
          <span className="w-3 shrink-0" />
        )}
        <span>{topic.name}</span>
      </button>
      {expanded && hasChildren && (
        <div>
          {topic.children!.map((child) => (
            <TopicBranch
              key={child.id}
              topic={child}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function TaxonomyTree({
  curricula,
  subjects,
  topics,
  onSelectCurriculum,
  onSelectSubject,
  onSelectTopic,
}: TaxonomyTreeProps) {
  const [expandedCurriculum, setExpandedCurriculum] = useState(true);
  const [expandedSubjects, setExpandedSubjects] = useState(true);

  return (
    <div className="space-y-1 text-sm">
      {/* Curricula */}
      <div>
        <button
          type="button"
          className="flex items-center gap-1 w-full text-left px-2 py-1.5 font-medium hover:bg-accent rounded-sm"
          onClick={() => setExpandedCurriculum(!expandedCurriculum)}
        >
          {expandedCurriculum ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
          Curricula
        </button>
        {expandedCurriculum &&
          curricula.map((c) => (
            <button
              key={c.id}
              type="button"
              className="flex items-center gap-1 w-full text-left px-6 py-1 hover:bg-accent rounded-sm"
              onClick={() => onSelectCurriculum?.(c.id)}
            >
              {c.code} — {c.name}
            </button>
          ))}
      </div>

      {/* Subjects */}
      <div>
        <button
          type="button"
          className="flex items-center gap-1 w-full text-left px-2 py-1.5 font-medium hover:bg-accent rounded-sm"
          onClick={() => setExpandedSubjects(!expandedSubjects)}
        >
          {expandedSubjects ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
          Subjects
        </button>
        {expandedSubjects &&
          subjects.map((s) => (
            <button
              key={s.id}
              type="button"
              className="flex items-center gap-1 w-full text-left px-6 py-1 hover:bg-accent rounded-sm"
              onClick={() => onSelectSubject?.(s.id)}
            >
              {s.code} — {s.name}
            </button>
          ))}
      </div>

      {/* Topics tree */}
      <div className="pt-2 border-t">
        {topics.map((topic) => (
          <TopicBranch
            key={topic.id}
            topic={topic}
            onSelect={onSelectTopic}
          />
        ))}
      </div>
    </div>
  );
}