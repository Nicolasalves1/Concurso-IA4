from PyQt5.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal(str, int, list)

    def __init__(self, text, empresa_demands):
        super().__init__()
        self.text = text.upper()
        self.empresa_demands = empresa_demands

    def run(self):
        self.update_progress.emit(10)

        escolaridade = {
            "ENSINO FUNDAMENTAL INCOMPLETO": 0,
            "ENSINO FUNDAMENTAL COMPLETO": 1,
            "ENSINO MÉDIO INCOMPLETO": 2,
            "ENSINO MÉDIO COMPLETO": 3,
            "CURSO TÉCNICO": 4,
            "TECNÓLOGO": 5,
            "ENSINO SUPERIOR INCOMPLETO": 6,
            "ENSINO SUPERIOR COMPLETO": 7,
            "PÓS-GRADUAÇÃO": 8,
            "MBA": 9,
            "MESTRADO": 10,
            "DOUTORADO": 11,
            "PÓS-DOUTORADO": 12
        }

        cursos_tecnologia = [
            "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS", "CIÊNCIA DA COMPUTAÇÃO", "ENGENHARIA DA COMPUTAÇÃO",
            "ENGENHARIA DE SOFTWARE", "SISTEMAS DE INFORMAÇÃO", "REDES DE COMPUTADORES",
            "SEGURANÇA DA INFORMAÇÃO", "BANCO DE DADOS", "TECNOLOGIA DA INFORMAÇÃO", "INFORMÁTICA",
            "DESENVOLVIMENTO WEB", "DESENVOLVIMENTO MOBILE", "JOGOS DIGITAIS", "BIG DATA",
            "INTELIGÊNCIA ARTIFICIAL", "COMPUTAÇÃO EM NUVEM", "ROBÓTICA", "AUTOMAÇÃO INDUSTRIAL",
            "MACHINE LEARNING", "PROCESSAMENTO DE DADOS", "GESTÃO DA TECNOLOGIA DA INFORMAÇÃO",
            "ADMINISTRAÇÃO DE SISTEMAS", "DEVOPS", "PROGRAMAÇÃO", "INFORMÁTICA BIOMÉDICA"
        ]

        keywords = [
            "Desenvolvimento Web", "Desenvolvimento Backend", "Desenvolvimento Frontend", "HTML", "CSS",
            "JavaScript", "PHP", "Python", "Java", "React", "Node.js", "Laravel", "MySQL", "PostgreSQL",
            "MongoDB", "API REST", "Git", "GitHub", "Controle de Versão", "Scrum", "Metodologias Ágeis",
            "UI/UX", "Docker", "Linux", "TypeScript", "Firebase", "Segurança da Informação",
            "Integração de APIs", "Testes Automatizados", "Programação Orientada a Objetos (POO)",
            "Clean Code", "Design Patterns", "Responsividade", "SEO Técnico", "Deploy", "Cloud Computing",
            "AWS", "Azure", "CI/CD"
        ]

        resultado = ""
        compatividade = 100
        faltando = [d for d in self.empresa_demands if d not in self.text]

        if faltando:
            resultado += f"\nQualidades técnicas não compatíveis, faltam: {', '.join(faltando)}\n"
            compatividade -= 20 * len(faltando)
        else:
            resultado += "\nTodas as qualidades técnicas estão presentes!\n"

        resultado += f"Compatibilidade técnica: {compatividade}%\n"
        resultado += (
            "Candidato está à altura da empresa (técnico)\n"
            if compatividade >= 70 else
            "Candidato não está à altura da empresa (técnico)\n"
        )

        self.update_progress.emit(40)

        keywords_found_list = [k for k in keywords if k.upper() in self.text]
        keywords_found = len(keywords_found_list)
        keywords_percent = round((keywords_found / len(keywords)) * 25, 2)

        resultado += f"\n--- Verificação de palavras-chave ---\n"
        resultado += f"Palavras-chave encontradas: {keywords_found}/{len(keywords)}\n"
        resultado += f"Compatibilidade geral com palavras-chave: {keywords_percent}%\n"
        resultado += f"Lista de palavras-chave encontradas:\n- " + "\n- ".join(keywords_found_list) + "\n"


        self.update_progress.emit(60)

        nivel_max = -1
        nivel_nome = "Não especificado"
        for nivel, valor in escolaridade.items():
            if nivel in self.text and valor > nivel_max:
                nivel_max = valor
                nivel_nome = nivel.title()

        resultado += f"\n--- Escolaridade ---\nNível de escolaridade identificado: {nivel_nome}\n"

        curso_encontrado = next((c.title() for c in cursos_tecnologia if c in self.text), None)
        resultado += f"\n--- Curso na área de tecnologia ---\n"
        resultado += (
            f"Curso de tecnologia encontrado: {curso_encontrado}\n"
            if curso_encontrado else
            "Nenhum curso de tecnologia identificado.\n"
        )

        self.update_progress.emit(90)

        total = compatividade + keywords_percent / 2
        if compatividade >= 100:
         resultado += f"\nCompatibilidade Total: {total}%\n"

        self.update_progress.emit(100)
        self.finished.emit(resultado, int(total), faltando)
