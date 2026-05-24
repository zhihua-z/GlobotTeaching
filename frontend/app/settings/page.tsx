"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { User, BookOpen, Bell, Download } from "lucide-react";

export default function SettingsPage() {
  const [dailyHours, setDailyHours] = useState("3.0");
  const [targetDate, setTargetDate] = useState("2026-09-XX");
  const [email, setEmail] = useState("zhihua@example.com");
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await new Promise((r) => setTimeout(r, 500));
    setSaving(false);
  };

  const handleExport = async () => {
    await new Promise((r) => setTimeout(r, 1000));
    alert("数据导出功能将在后端就绪后可用。");
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">设置</h1>
      
      <Tabs defaultValue="profile">
        <TabsList className="mb-6">
          <TabsTrigger value="profile">个人信息</TabsTrigger>
          <TabsTrigger value="study">学习偏好</TabsTrigger>
          <TabsTrigger value="notifications">提醒推送</TabsTrigger>
          <TabsTrigger value="export">数据导出</TabsTrigger>
        </TabsList>

        {/* Tab 1: 个人信息 */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" /> 个人信息
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">邮箱</Label>
                <Input
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                />
              </div>
              <div className="space-y-2">
                <Label>角色</Label>
                <div className="text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
                  学生 (Zhihua)
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "保存中..." : "保存"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: 学习偏好 */}
        <TabsContent value="study">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" /> 学习偏好
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dailyHours">每日可学习 (小时)</Label>
                  <Input
                    id="dailyHours"
                    type="number"
                    step="0.5"
                    min="0.5"
                    max="12"
                    value={dailyHours}
                    onChange={(e) => setDailyHours(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="targetDate">目标考试日期</Label>
                  <Input
                    id="targetDate"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    placeholder="YYYY-MM-DD"
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "保存中..." : "保存"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: 提醒推送 */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" /> 提醒推送
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={emailEnabled}
                  onChange={(e) => setEmailEnabled(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">邮件通知提醒</span>
              </label>
              <p className="text-xs text-gray-500 ml-6">
                每天推送复习提醒、学习报告等
              </p>
              <div className="flex justify-end">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? "保存中..." : "保存"}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 4: 数据导出 */}
        <TabsContent value="export">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5" /> 数据导出
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
                导出您的全部学习数据，包括答题记录、学习进度、个人知识图谱等。
              </p>
              <div className="flex justify-end">
                <Button onClick={handleExport}>
                  <Download className="w-4 h-4 mr-1" /> 导出全部数据 (JSON)
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}