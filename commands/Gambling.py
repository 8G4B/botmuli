import discord
from discord.ext import commands

from datetime import datetime
import json
import os
import secrets
import random
import threading

class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}
        self.balances = {}
        self.jackpot = 0
        self.data_file = 'gambling_data.json'
        self.locks = {}
        self.global_lock = threading.Lock()
        self._load_data()  

    def _get_lock(self, user_id):
        with self.global_lock:
            if user_id not in self.locks:
                self.locks[user_id] = threading.Lock()
            return self.locks[user_id]

    def _load_data(self):
        with self.global_lock:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r') as f:
                        data = json.load(f)
                        self.balances = {int(k): v for k, v in data.get('balances', {}).items()}
                        self.jackpot = data.get('jackpot', 0)
            except Exception as e:
                print(f"_load_data: {e}")

    def _save_data(self):
        with self.global_lock:
            try:
                data = {
                    'balances': self.balances,
                    'jackpot': self.jackpot
                }
                with open(self.data_file, 'w') as f:
                    json.dump(data, f)
            except Exception as e:
                print(f"_save_data: {e}")

    def _validate_bet(self, bet):
        if bet is None or bet < 100:
            return discord.Embed(
                title="❗ 오류",
                description="100원 이상 베팅하세요",
                color=discord.Color.red()
            )
        return None

    def _validate_coin_guess(self, guess):
        if guess not in ["앞", "뒤"]:
            return discord.Embed(
                title="❗ 오류", 
                description="**'앞'**이랑 **'뒤'**만 입력해라...",
                color=discord.Color.red()
            )
        return None

    def _validate_dice_guess(self, guess):
        if guess not in [str(i) for i in range(1, 7)]:
            return discord.Embed(
                title="❗ 오류",
                description="**1부터 6까지 숫자**만 입력해라...",
                color=discord.Color.red()
            )
        return None

    def _play_game(self, author_id, author_name, guess, result, bet, multiplier, game_type):
        with self._get_lock(author_id):
            is_correct = guess == result
            winnings = int(bet * multiplier) if is_correct else -bet
            
            current_balance = self.balances.get(author_id, 0)
            if is_correct:
                self.balances[author_id] = current_balance + winnings
            else:
                self.balances[author_id] = current_balance + winnings
                with self.global_lock:
                    self.jackpot += abs(winnings)
                
            self._save_data()
            return self._create_game_embed(author_name, is_correct, guess, result, bet, winnings, author_id, game_type)

    def _check_game_cooldown(self, user_id, game_type):
        current_time = datetime.now()
        cooldown_key = f"{game_type}_{user_id}"
        last_used = self.cooldowns.get(cooldown_key)
        
        if last_used and (current_time - last_used).total_seconds() < 5:
            remaining = 5 - int((current_time - last_used).total_seconds())
            return discord.Embed(
                title="⏳️ 쿨타임",
                description=f"{remaining}초 후에 다시 시도해주세요.",
                color=discord.Color.red()
            )
        self.cooldowns[cooldown_key] = current_time
        return None

    @commands.command(name="도박.동전", description="동전 던지기")
    async def coin(self, ctx, guess: str = None, bet: int = None):
        with self._get_lock(ctx.author.id):
            if cooldown_embed := self._check_game_cooldown(ctx.author.id, "coin"):
                embed = cooldown_embed
            elif error_embed := self._validate_coin_guess(guess):
                embed = error_embed
            elif error_embed := self._validate_bet(bet):
                embed = error_embed
            elif bet > self.balances.get(ctx.author.id, 0):
                embed = discord.Embed(
                    title="❗ 오류",
                    description="돈이 부족해...",
                    color=discord.Color.red()
                )
            else:
                result = secrets.choice(["앞", "뒤"])
                embed = self._play_game(ctx.author.id, ctx.author.name, guess, result, bet, random.uniform(0.8, 1.8), "coin")
            await ctx.reply(embed=embed)

    @commands.command(name="도박.주사위", description="주사위")
    async def dice(self, ctx, guess: str = None, bet: int = None):
        with self._get_lock(ctx.author.id):
            if cooldown_embed := self._check_game_cooldown(ctx.author.id, "dice"):
                embed = cooldown_embed
            elif error_embed := self._validate_dice_guess(guess):
                embed = error_embed
            elif error_embed := self._validate_bet(bet):
                embed = error_embed
            elif bet > self.balances.get(ctx.author.id, 0):
                embed = discord.Embed(
                    title="❗ 오류",
                    description="돈이 부족해...",
                    color=discord.Color.red()
                )
            else:
                result = secrets.choice([str(i) for i in range(1, 7)])
                embed = self._play_game(ctx.author.id, ctx.author.name, guess, result, bet, random.uniform(5.5, 6.5), "dice")
            await ctx.reply(embed=embed)

    @commands.command(name="도박.잭팟", description="잭팟")
    async def jackpot(self, ctx, bet: int = None):
        with self._get_lock(ctx.author.id):
            if cooldown_embed := self._check_game_cooldown(ctx.author.id, "jackpot"):
                embed = cooldown_embed
            elif bet is None or bet < 1000:
                embed = discord.Embed(
                    title="❗ 오류",
                    description="1000원 이상 베팅하세요",
                    color=discord.Color.red()
                )
            elif bet > self.balances.get(ctx.author.id, 0):
                embed = discord.Embed(
                    title="❗ 오류",
                    description="돈이 부족해...",
                    color=discord.Color.red()
                )
            else:
                with self.global_lock:
                    current_balance = self.balances.get(ctx.author.id, 0)
                    self.balances[ctx.author.id] = current_balance - bet
                    self.jackpot += bet
                    
                    if secrets.randbelow(100) <= 1:
                        winnings = self.jackpot // 10
                        self.balances[ctx.author.id] = current_balance - bet + winnings
                        self.jackpot -= winnings
                        embed = discord.Embed(
                            title=f"🎉 {ctx.author.name} 당첨",
                            description=f"축하합니다!\n## 수익: {winnings}원\n- 재산: {self.balances[ctx.author.id]}원(+{winnings})",
                            color=discord.Color.gold()
                        )
                    else:
                        embed = discord.Embed(
                            title=f"🎰 {ctx.author.name} 잭팟 실패ㅋ",
                            description=f"\n- 현재 잭팟: {self.jackpot}원 \n## 수익: -{bet}원\n- 재산: {self.balances[ctx.author.id]}원",
                            color=discord.Color.red()
                        )
                    
                    self._save_data()
            await ctx.reply(embed=embed)
        
    @commands.command(name="도박.노동", aliases=['도박.일', '도박.돈'], description="도박.노동")
    async def get_money(self, ctx):
        with self._get_lock(ctx.author.id):
            current_time = datetime.now()
            last_used = self.cooldowns.get(ctx.author.id)
            
            if last_used and (current_time - last_used).total_seconds() < 60:
                remaining = 60 - int((current_time - last_used).total_seconds())
                embed = discord.Embed(
                    title="힘들어서 쉬는 중 ㅋ",
                    description=f"{remaining}초 후에 다시 시도해주세요.",
                    color=discord.Color.red()
                )
            else:
                amount = random.randint(100, 2000)
                self.balances[ctx.author.id] = self.balances.get(ctx.author.id, 0) + amount
                embed = discord.Embed(
                    title=f"☭ {ctx.author.name} 노동",
                    description=f"정당한 노동을 통해 {amount}원을 벌었다. \n- 재산: {self.balances.get(ctx.author.id, 0)}원(+{amount})",
                    color=discord.Color.green()
                )
                self.cooldowns[ctx.author.id] = current_time
                self._save_data()  
            
            await ctx.reply(embed=embed)

    @commands.command(name="도박.지갑", aliases=['도박.잔액', '도박.직바'], description="잔액 확인")
    async def check_balance(self, ctx):
        with self._get_lock(ctx.author.id):
            balance = self.balances.get(ctx.author.id, 0)
            embed = discord.Embed(
                title=f"💰 {ctx.author.name}의 지갑",
                description=f"현재 잔액: {balance}원",
                color=discord.Color.blue()
            )
            await ctx.reply(embed=embed)

    @commands.command(name="도박.랭킹", description="랭킹")
    async def ranking(self, ctx):
        with self.global_lock:
            sorted_balances = sorted(self.balances.items(), key=lambda item: item[1], reverse=True)
            top_3 = sorted_balances[:3]
            
            description = "\n".join([f"{i+1}. <@{user_id}>: {balance}원" for i, (user_id, balance) in enumerate(top_3)])

            
            embed = discord.Embed(
                title="🏅 상위 3명 랭킹",
                description=description if description else "랭킹이 없습니다.",
                color=discord.Color.blue()
            )
            await ctx.reply(embed=embed)
        
    @commands.command(name="도박.전체랭킹", description="전체 랭킹")
    async def all_ranking(self, ctx):
        with self.global_lock:
            sorted_balances = sorted(self.balances.items(), key=lambda item: item[1], reverse=True)
            
            description = "\n".join([f"{i+1}. <@{user_id}>: {balance}원" for i, (user_id, balance) in enumerate(sorted_balances)])

            embed = discord.Embed(
                title="🏅 전체 랭킹",
                description=description,
                color=discord.Color.blue()
            )
            await ctx.reply(embed=embed)

    def _create_game_embed(self, author_name, is_correct, guess, result, bet=None, winnings=None, author_id=None, game_type=None):
        title = f"{'🪙' if game_type == 'coin' else '🎲' if game_type == 'dice' else '🎰'} {author_name} {'맞음 ㄹㅈㄷ' if is_correct else '틀림ㅋ'}"
        color = discord.Color.green() if is_correct else discord.Color.red()
        
        description_parts = [
            f"- 예측: {guess}",
            f"- 결과: {result}"
        ]
        
        if bet is not None:
            multiplier = round(winnings / bet, 2) if winnings > 0 else -1
            balance = self.balances.get(author_id, 0)
            sign = '+' if winnings > 0 else ''
            
            description_parts.extend([
                f"## 수익: {bet}원 × {multiplier} = {winnings}원",
                f"- 재산: {balance}원({sign}{winnings})"
            ])
            
        description = "\n".join(description_parts)
            
        return discord.Embed(
            title=title,
            description=description,
            color=color
        )
