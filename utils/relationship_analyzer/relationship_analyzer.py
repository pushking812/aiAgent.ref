def main():
    parser = argparse.ArgumentParser(
        description='Анализатор полного дерева отношений Python-проекта'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Путь к файлу или директории для анализа'
    )
    parser.add_argument(
        '-r', '--project-root',
        help='Корневая директория проекта (по умолчанию определяется автоматически)'
    )
    parser.add_argument(
        '-t', '--tree',
        action='store_true',
        help='Построить иерархическое дерево'
    )
    parser.add_argument(
        '-g', '--graph',
        action='store_true',
        help='Построить граф зависимостей'
    )
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Экспортировать в JSON'
    )
    parser.add_argument(
        '-f', '--format',
        choices=['png', 'svg', 'pdf'],
        default='png',
        help='Формат графического вывода'
    )
    parser.add_argument(
        '--exclude',
        nargs='+',
        default=[],
        help='Директории для исключения'
    )
    
    # Если только help запрошен, показываем справку
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # Определяем корень проекта
    if args.project_root:
        # Используем указанный корень проекта
        root_path = Path(args.project_root).absolute()
        if not root_path.exists():
            print(f"❌ Ошибка: указанная корневая директория '{args.project_root}' не существует")
            sys.exit(1)
    else:
        # Определяем корень автоматически
        input_path = Path(args.path).absolute()
        
        if input_path.is_file():
            # Если указан файл, берем его родительскую директорию
            root_path = input_path.parent
        else:
            # Если указана директория, используем ее
            root_path = input_path
        
        # Проверяем существование пути
        if not root_path.exists():
            print(f"❌ Ошибка: путь '{args.path}' не существует")
            sys.exit(1)
    
    print(f"📁 Корень проекта: {root_path}")
    
    # Если указан конкретный файл, сообщаем об этом
    if Path(args.path).is_file():
        print(f"📄 Анализируемый файл: {args.path}")
    else:
        print(f"📄 Анализируемая директория: {args.path}")
    
    # Создаем анализатор
    analyzer = FullRelationshipAnalyzer(root_path, exclude_dirs=args.exclude)
    
    try:
        # Выполняем анализ
        analyzer.analyze_project()
        
        # Проверяем, есть ли модули для анализа
        if len(analyzer.modules) == 0:
            print(f"\n⚠️  В указанном пути не найдено Python-модулей для анализа")
            print("   Проверьте путь и исключения (--exclude)")
            print("\nИспользуйте --help для просмотра справки:")
            print("  python relationship_analyzer.py --help")
            return
        
        # Строим дерево (текстовое)
        if args.tree:
            analyzer.create_hierarchical_tree_text()
        
        # Строим графическое дерево
        if args.graph and HAS_GRAPHVIZ:
            analyzer.create_full_tree(f"project_tree_{args.format}")
        elif args.graph and not HAS_GRAPHVIZ:
            print("\nДля графического вывода установите graphviz")
            print("pip install graphviz")
            print("Или используйте только текстовый вывод с флагом -t")
        
        # Экспортируем в JSON
        if args.json:
            analyzer.export_to_json()
        
        # Если не указаны флаги, показываем краткую справку
        if not any([args.tree, args.graph, args.json]):
            print("\n✅ Анализ завершен. Используйте флаги для вывода результатов:")
            print("  -t, --tree        : Текстовое дерево отношений")
            print("  -g, --graph       : Графическое дерево (требует graphviz)")
            print("  -j, --json        : Экспорт в JSON")
            print("\nПример: python relationship_analyzer.py . -t -g")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)